---
name: authed-browser-runner
description: Run repeatable headless-browser checks against a site behind a login wall (HTTP Basic Auth, SSO, or session cookie) by authenticating once and attaching over CDP for every run after. Covers the auth-once session model, a reference Playwright runner, 2x screenshots, and the collision and auth-capture gotchas that waste the most time. Use it when a page needs a login your script can't drive and you'll check it more than once.
argument-hint: "[target URL]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Authed browser runner

Drive a real browser against a site behind a login wall — HTTP Basic Auth, an SSO gateway, or a session cookie — and run repeatable checks (UI smoke tests, keyboard and click flows, screenshots, DOM assertions) **without logging in again on every run**.

The model is **auth once, attach many**: a human completes one visible login, a headless browser stays alive on a Chrome DevTools Protocol (CDP) port, and each run attaches to that same browser over CDP. `curl` and freshly launched browser profiles get a `401`; a long-lived, already-authenticated browser process does not.

## When to use

- The page needs a login your script can't drive — a Basic Auth prompt, an SSO redirect, 2FA.
- You'll run more than one check against the same origin and don't want to re-auth each time.
- You need real-browser behavior — JavaScript, keyboard, clicks, modals — not just an HTTP client.
- You want deterministic CLI/Node scripts rather than an interactive browser tool.

Skip it if an unauthenticated `curl` or a single fresh Playwright launch already reaches the page.

## The model in one paragraph

Browser auth is held **in the running browser process**, not on disk. HTTP Basic Auth in particular lives in memory and is dropped on relaunch, so re-launching a saved profile re-prompts or fails with `ERR_INVALID_AUTH_CREDENTIALS`. The fix is to keep **one** authenticated browser process alive and reuse it: log in once, prime the origin's credential cache, expose a CDP port, and have every later run `connectOverCDP` and reuse the existing context. The unit of reuse is the *process*, not the profile directory.

## Prerequisites

- Node.js and Playwright available (`npm i -D playwright`, or reuse an existing install and `require()` it by absolute path if your script lives outside that install).
- Chrome or Chromium.
- Pick an **unused** CDP port per session (e.g. `9333`) and a **fresh, unique** profile directory per session. Both matter — see [Troubleshooting](#troubleshooting).

## Workflow

### 1. Start a long-lived authenticated session

Run a helper that opens one visible window for the login, then keeps a headless browser alive on a CDP port. There are two auth shapes:

**Cookie / SSO auth** — the session is stored in the profile, so a persistent profile is enough: launch headed with `launchPersistentContext(profileDir)`, log in once, then reuse that same profile directory headless. This is the simple case.

**HTTP Basic Auth** — the credentials live in memory, not the profile, so a saved profile won't carry them. Capture them from the live login and hold them in the running process instead:

```js
// start-session.js
//   node start-session.js --url https://app.example.com/ --cdp-port 9333
const { chromium } = require('playwright');
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : d; };

const url = arg('--url');
const cdpPort = Number(arg('--cdp-port', '9333'));
const origin = new URL(url).origin;

const waitFor = async (cond, ms, msg) => {
  const end = Date.now() + ms;
  while (Date.now() < end) { if (await cond()) return; await new Promise(r => setTimeout(r, 500)); }
  throw new Error(msg);
};

(async () => {
  // (a) Visible bootstrap: a human completes the login; observe the Basic Auth header.
  const bootstrap = await chromium.launch({ headless: false });
  const bpage = await (await bootstrap.newContext()).newPage();
  let captured = null;
  bpage.on('request', req => {
    const h = req.headers()['authorization'];
    if (h && h.startsWith('Basic ') && req.url().startsWith(origin)) captured = h;
  });
  console.log(`Log in to ${origin} in the window that just opened...`);
  await bpage.goto(url, { waitUntil: 'domcontentloaded', timeout: 0 }).catch(() => {});
  await waitFor(() => captured, 5 * 60_000,
    'Basic Auth header not observed - use a FRESH profile so a real login prompt fires (see Troubleshooting).');
  await bootstrap.close();

  // (b) Headless long-lived session that reuses the captured credentials, on a CDP port.
  const [u, p] = Buffer.from(captured.split(' ')[1], 'base64').toString().split(':');
  const browser = await chromium.launch({ headless: true, args: [`--remote-debugging-port=${cdpPort}`] });
  const context = await browser.newContext({ httpCredentials: { username: u, password: p } });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' }); // prime the origin's in-memory auth cache
  console.log(`Session ready on http://127.0.0.1:${cdpPort} - leave this process running.`);
  await new Promise(() => {}); // stay alive until killed
})().catch(e => { console.error(e.message); process.exit(1); });
```

The captured username/password stay inside this process's memory — never written to disk, never printed. Give the human unlimited time to log in (`timeout: 0`), then poll `curl -s http://127.0.0.1:9333/json/version` for readiness before driving.

### 2. Attach and drive

Every later run attaches over CDP and reuses the **existing** context, which already holds the origin's cached auth. Never create a fresh context — a new one is unauthenticated.

```js
// drive.js  ->  node drive.js
const { chromium } = require('playwright');
const CDP = 'http://127.0.0.1:9333';
const TARGET = 'https://app.example.com/';

(async () => {
  const browser = await chromium.connectOverCDP(CDP);
  const context = browser.contexts()[0];                 // reuse the authed context
  const page = context.pages().find(p => p.url().startsWith(new URL(TARGET).origin))
            || await context.newPage();                   // new PAGE in that context, not a new context
  const errors = [];
  page.on('console', m => m.type() === 'error' && errors.push(m.text().slice(0, 200)));
  page.on('pageerror', e => errors.push('pageerror: ' + e.message.slice(0, 200)));

  const resp = await page.goto(TARGET, { waitUntil: 'domcontentloaded' });
  console.log('status', resp && resp.status(), '| url', page.url());

  // ...drive the page: keyboard, clicks, assertions, screenshots. For example,
  // open a command modal and confirm it renders:
  //   await page.keyboard.press('Meta+k');
  //   await page.waitForTimeout(800);
  //   await page.screenshot({ path: 'out.png' });

  console.log('console errors:', JSON.stringify(errors));
  await page.close();          // close ONLY your page; never browser.close() on a CDP attach
  process.exit(0);             // self-exit - page.close() can hang, and macOS has no `timeout`
})().catch(e => { console.error(e.message); process.exit(1); });
```

### 3. Capture 2x screenshots (when you need sharp evidence)

`page.screenshot()` is 1x, which goes fuzzy after any downstream scaling. For retina evidence, drive CDP directly:

```js
const client = await page.context().newCDPSession(page);
await page.setViewportSize({ width: 1440, height: 1000 });
await client.send('Emulation.setDeviceMetricsOverride',
  { width: 1440, height: 1000, deviceScaleFactor: 2, mobile: false });
const shot = await client.send('Page.captureScreenshot',
  { format: 'png', clip: { x: 0, y: 0, width: 1440, height: 1000, scale: 1 } });
require('node:fs').writeFileSync('out@2x.png', Buffer.from(shot.data, 'base64'));
```

Use `deviceScaleFactor: 2` with `clip.scale: 1` — combining both gives a 4x image. Verify the saved pixel size afterward (a 1440x1000 viewport at 2x is a 2880x2000 PNG).

### 4. Tear down — scoped to your own session

```bash
pkill -f "remote-debugging-port=9333"      # your CDP port only
rm -rf /tmp/authed-session-*               # your profile dirs only
curl -s http://127.0.0.1:9333/json/version >/dev/null && echo "still up" || echo "clear"
```

Scope every kill to your port or URL. Never `pkill` the helper by script name alone if anyone else might be running a session.

## Troubleshooting

These are the failures that eat the most time; most trace back to profile or port reuse.

| Symptom | Cause | Fix |
|---|---|---|
| `Basic Auth header not observed` | The profile already had cached credentials (reused/polluted profile, or the OS keychain auto-filled), so no fresh `401 -> login` fired to capture. | Use a **brand-new, unique** profile directory so a real login prompt appears. |
| Launcher exits immediately / no CDP endpoint | The CDP port was already taken by another session. | Pick an **unused** port; don't assume a default is free. |
| `ERR_INVALID_AUTH_CREDENTIALS` after relaunch | Basic Auth is in-memory; relaunching a saved profile drops it. | Don't chase profile persistence — keep the **process** alive and attach to it. |
| `401` even though you "have a session" | Credentials are **per-origin**; a session for one host doesn't cover another. | Start a **separate session per origin**. |
| Attached page is unauthenticated | You made a **new** context via `connectOverCDP`; it doesn't share the primed auth cache. | Reuse `browser.contexts()[0]` and open a new **page**, not a new context. |
| The session dies during cleanup | An unscoped `pkill`, or `browser.close()` on a CDP attach, tore down a shared browser. | Close only your page; scope kills to your port/URL. |
| A modal "won't close" in your assertions | You checked DOM **presence**; many modals stay mounted and just hide. | Check real visibility (`el.offsetParent !== null && getComputedStyle(el).display !== 'none'`), not element existence. |
| Script hangs at the end | `page.close()` on a CDP-attached page can block. | End with `process.exit(0)`. macOS has no `timeout` to wrap it. |
| Helper waits forever after login | It's blocking on an app-specific selector that never appears on your page. | Don't gate readiness on app UI; wait for the CDP endpoint or a generic load signal. |

## What not to do

- Don't relaunch fresh browser profiles for every check — that re-prompts for auth and wastes the human's time.
- Don't run follow-up checks in the visible login window — it's a short bootstrap that closes once auth is captured.
- Don't copy browser profiles or cookies between runs as an auth workaround; browser auth can be tied to the live process, and copies fail or leak state.
- Don't `browser.close()` on a CDP attach, and don't `pkill` the helper unscoped — either can kill a session someone else is using.

## Security

- **Never read, print, store, or commit credential or cookie values.** Capture the login through a real browser prompt and keep any derived credentials in process memory only. Inspecting cookie *host names* or counts is fine; values are not.
- Prefer manual browser login over feeding secrets to a script. If a workflow seems to need a pasted secret, stop and find a reference (an env-var name, a secret-store key) instead.
- When saving screenshots or DOM as evidence, classify it against where it will be shared: never attach authenticated, non-public content to a public destination.
