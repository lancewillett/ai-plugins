---
name: playwright-ui-check
description: Verify a login-gated UI loads and behaves correctly, to validate product changes fast, by logging in once and attaching a headless browser over CDP for every check after. Covers the auth-once session model, a reference Playwright runner, 2x screenshots, and the collision and auth-capture gotchas that waste the most time. Use it when a page needs a login your script can't drive and you'll check it more than once.
argument-hint: "[target URL]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Playwright UI check

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
- Prefer an existing repository helper when one exists. It usually encodes the site's login and readiness behavior better than a new generic script.

## Workflow

### 1. Start a long-lived authenticated session

Run a helper that opens one visible window for the login, then keeps a headless browser alive on a CDP port. There are two auth shapes:

**Cookie / SSO auth** — the session is stored in the profile, so a persistent profile is enough: launch headed with `launchPersistentContext(profileDir)`, log in once, then reuse that same profile directory headless. This is the simple case — it relaunches per run and needs no CDP port, so the attach and teardown machinery below applies mainly to the Basic Auth long-lived-session path.

**HTTP Basic Auth** — the credentials live in memory, not the profile, so a saved profile won't carry them. Capture them from the live login and hold them in the running process instead:

```js
// start-session.js
//   node start-session.js --url https://app.example.com/ --cdp-port 9333 [--profile-dir DIR]
const { chromium } = require('playwright');
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : d; };

const url = arg('--url');
const cdpPort = Number(arg('--cdp-port', '9333'));
// A FRESH profile dir per run is what makes a real Basic Auth prompt fire (see Troubleshooting).
const profileDir = arg('--profile-dir', '/tmp/authed-session-' + Date.now());
const origin = new URL(url).origin;
let bootstrap;
let browser;
let context;

const shutdown = async (code = 0) => {
  await context?.close().catch(() => {});
  await browser?.close().catch(() => {});
  await bootstrap?.close().catch(() => {});
  process.exit(code);
};
process.on('SIGINT', () => void shutdown(0));
process.on('SIGTERM', () => void shutdown(0));

const waitFor = async (cond, ms, msg) => {
  const end = Date.now() + ms;
  while (Date.now() < end) { if (await cond()) return; await new Promise(r => setTimeout(r, 500)); }
  throw new Error(msg);
};

(async () => {
  // (a) Visible bootstrap in the fresh profile dir: a human completes the login and we
  //     observe the Basic Auth header. A reused/primed profile auto-auths, so the header
  //     is never seen — which is exactly why the profile must be fresh.
  bootstrap = await chromium.launchPersistentContext(profileDir, { headless: false });
  const bpage = bootstrap.pages()[0] || await bootstrap.newPage();
  let captured = null;
  bpage.on('request', req => {
    const h = req.headers()['authorization'];
    if (h && h.startsWith('Basic ') && new URL(req.url()).origin === origin) captured = h;
  });
  console.log(`Log in to ${origin} in the window that just opened...`);
  await bpage.goto(url, { waitUntil: 'domcontentloaded', timeout: 0 }).catch(() => {});
  await waitFor(() => captured, 5 * 60_000,
    'Basic Auth header not observed - use a FRESH profile so a real login prompt fires (see Troubleshooting).');
  await bootstrap.close();

  // (b) Headless long-lived session that reuses the captured credentials, on a CDP port.
  const decoded = Buffer.from(captured.split(' ')[1], 'base64').toString();
  const separator = decoded.indexOf(':');
  if (separator < 0) throw new Error('Malformed Basic Auth credentials.');
  const u = decoded.slice(0, separator);
  const p = decoded.slice(separator + 1); // passwords may contain colons
  browser = await chromium.launch({ headless: true, args: [`--remote-debugging-port=${cdpPort}`] });
  context = await browser.newContext({ httpCredentials: { username: u, password: p } });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' }); // prime the origin's in-memory auth cache
  console.log(`Session ready on http://127.0.0.1:${cdpPort}; helper PID ${process.pid} - leave this process running.`);
  await new Promise(() => {}); // stay alive until killed
})().catch(async e => { console.error(e.message); await shutdown(1); });
```

The captured username/password stay inside this process's memory — never written to disk, never printed. The visible login runs in a fresh `--profile-dir` (default `/tmp/authed-session-<timestamp>`) so a real prompt fires; that directory is what teardown's `rm -rf /tmp/authed-session-*` removes. The example allows five minutes for login; adjust that timeout when needed. Poll `curl -s http://127.0.0.1:9333/json/version` for readiness before driving.

Keep the helper in a dedicated terminal or supervised terminal-multiplexer session. Short-lived agent command runners may send it `SIGTERM` as soon as their command session ends, even after it printed "ready." Record the helper PID and CDP port so teardown can target both the parent helper and its Chrome child.

#### Pin the target build before and after long runs

Authentication proves access, not that the intended build is loaded. Record the expected branch, commit, or build identifier and re-verify it immediately before the first probe and again after long runs — sync or deploy processes can silently swap the checkout mid-test. Treat every result as invalid if the code version (or a sandbox-versus-production routing marker, where one exists) drifted.

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

`domcontentloaded` means the page shell loaded; it does not mean every API request or streamed result settled. Wait for an app-specific completion signal before asserting counts, JSON validity, errors, or screenshots. Keep promises for asynchronous `response` checks and await them before navigating away; otherwise an intentional navigation can abort a late response and look like invalid JSON.

Set explicit timeouts from the endpoint's observed latency; a search that normally takes 70 seconds needs at least a 120-second test timeout. For JSON endpoints, check the HTTP status and `content-type` before parsing. If parsing fails, report a short response prefix so an HTML error page is distinguishable from malformed JSON.

For bounded aggregate or paginated views, test continuation too. A valid source result may be absent from the first batch and appear only after **More**, **Next**, or scrolling. Do not classify it as missing until the relevant continuation has settled.

### 3. Capture 2x screenshots (when you need sharp evidence)

`page.screenshot()` uses the page's current device scale factor. A default CDP-attached context is commonly 1x, which goes fuzzy after downstream scaling. To force retina evidence on an existing attached page, drive CDP directly:

```js
const client = await page.context().newCDPSession(page);
await page.setViewportSize({ width: 1440, height: 1000 });
await client.send('Emulation.setDeviceMetricsOverride',
  { width: 1440, height: 1000, deviceScaleFactor: 2, mobile: false });
const shot = await client.send('Page.captureScreenshot',
  { format: 'png', clip: { x: 0, y: 0, width: 1440, height: 1000, scale: 1 } });
require('node:fs').writeFileSync('out@2x.png', Buffer.from(shot.data, 'base64'));
```

Use `deviceScaleFactor: 2` with `clip.scale: 1`. Combining DPR 2 with `clip.scale: 2` would create an unwanted 4x image, so keep `clip.scale` at 1. Verify the saved pixel size afterward (a 1440x1000 viewport at 2x is a 2880x2000 PNG).

### 4. Tear down — scoped to your own session

```bash
kill <helper-pid>                           # graceful parent + browser shutdown
sleep 2
pkill -f "remote-debugging-port=9333"      # fallback: your CDP port only
rm -rf /tmp/authed-session-*               # your profile dirs only
curl -s http://127.0.0.1:9333/json/version >/dev/null && echo "still up" || echo "clear"
ps -p <helper-pid> >/dev/null && echo "helper still up" || echo "helper clear"
```

Signal the helper first so its cleanup handlers can close Chrome, then verify the PID and port separately. Scope every fallback kill to your port or URL — never `pkill` the helper by script name alone if anyone else might be running a session.

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
| A repo's own helper never reports ready | It gates readiness on an app-specific selector (app UI) your page doesn't render. | Don't gate on app UI; wait for a generic load signal or the CDP endpoint becoming reachable. |
| Helper printed "ready" and then vanished | The agent's command session ended and terminated its child process. | Run the helper in a dedicated persistent terminal; verify its PID and CDP endpoint before every smoke run. |
| The page shows the default build instead of the PR | A deployment or sync process changed the target checkout during testing. | Pin and re-check the branch, commit, or build identifier before and after probes. |
| A late API response looks like invalid JSON | The script navigated away before asynchronous response validation finished. | Wait for app settlement and await all response-check promises before navigation. |
| Teardown says complete but the port still listens | The terminal session stopped while the helper or Chrome child survived. | Signal the recorded helper PID, then verify both the PID and CDP port are gone. |
| The local browser cannot reach a development host | The machine driving Chrome lacks the required proxy, DNS, or hosts-file route. | Configure routing on the browser's machine. A proxy needed by the client does not belong on the target server. |

## What not to do

- Don't run follow-up checks in the visible login window — it's a short bootstrap that closes once auth is captured.
- Don't copy browser profiles or cookies between runs as an auth workaround; browser auth can be tied to the live process, and copies fail or leak state.
- Don't `browser.close()` on a CDP attach, and don't `pkill` the helper unscoped — either can kill a session someone else is using.

## Security

- **Never read, print, store, or commit credential or cookie values.** Capture the login through a real browser prompt and keep any derived credentials in process memory only. Inspecting cookie *host names* or counts is fine; values are not.
- **Don't embed credentials in the target URL** (`https://user:pass@host/`). A failed `goto` can surface the URL in an error, and `console.error(e.message)` would then print the secret — the one path in these scripts that could leak one.
- **Don't enable Playwright tracing, HAR recording, or video** on the credentialed context. They persist request headers (including `Authorization: Basic …`) to disk, breaking the in-memory-only guarantee.
- Prefer manual browser login over feeding secrets to a script. If a workflow seems to need a pasted secret, stop and find a reference (an env-var name, a secret-store key) instead.
- When saving screenshots or DOM as evidence, classify it against where it will be shared: never attach authenticated, non-public content to a public destination.
