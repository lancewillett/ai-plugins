---
name: visual-screenshots
description: Capture before/after screenshots for PRs with visual UI changes using Playwright.
argument-hint: "[PR URL or branch]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, mcp__playwright__browser_navigate, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_snapshot, mcp__playwright__browser_click, mcp__playwright__browser_type, mcp__playwright__browser_wait_for, mcp__playwright__browser_close, mcp__playwright__browser_resize, mcp__playwright__browser_evaluate, mcp__playwright__browser_run_code_unsafe, mcp__playwright__browser_file_upload
---

# Visual screenshots

Capture before/after screenshots for PRs that change UI — CSS, components, layouts, templates, themes.

## When to use

- Changes to CSS, SCSS, or styled-components
- React/PHP component changes with visual output
- Theme or template modifications
- Layout or responsive design changes
- When a PR template asks for screenshots (Gutenberg, WooCommerce, Calypso)

## Workflow

### Step 1: Identify targets

Determine what to screenshot based on the changes:

1. **Read the repo's CLAUDE.md** for its `## Visual development` section — it lists the dev server command, key URLs, auth details, and screenshot targets.
2. **Analyze the diff** to identify which URLs/views are affected.
3. **Pick viewport sizes** — default to 1280x800 (desktop). Add 390x844 (mobile) if responsive styles changed.
4. **Set screenshot quality** — capture at 2x/device-scale quality by default so UI text remains readable in PRs.

### Step 2: Capture "before" screenshots

Before making code changes (or on the base branch):

1. Ensure the dev server is running (check the repo's CLAUDE.md for the command).
2. Navigate to each target URL.
3. Resize the viewport if needed.
4. Wait for the page to fully load — use `browser_wait_for` if there's dynamic content.
5. Take a screenshot at 2x/device-scale quality:

```
browser_take_screenshot → screenshots/before-{slug}.png
```

Use PNG format (`type: "png"`) when the screenshot contains UI text, code, tables, dense controls, or visual evidence where readability matters. JPEG is only acceptable for photo-heavy pages where compression artifacts will not hide the change.

Name screenshots with descriptive slugs: `before-front-page.png`, `before-editor-sidebar.png`, `before-mobile-nav.png`.

### Step 3: Make changes

Apply the code changes. Wait for hot reload or rebuild to complete.

If the dev server needs a restart, do that and wait for it to be ready.

### Step 4: Capture "after" screenshots

Same URLs and viewport sizes as the "before" shots:

```
browser_take_screenshot → screenshots/after-{slug}.png
```

### Step 5: Present results

Print a summary with file paths:

```
Screenshots saved to ./screenshots/

| View | Before | After |
|------|--------|-------|
| Front page | screenshots/before-front-page.png | screenshots/after-front-page.png |
| Editor | screenshots/before-editor.png | screenshots/after-editor.png |
```

Then offer to add them to the PR: run **Step 6** to upload them automatically, or drag and drop the files into the GitHub PR description by hand.

### Step 6 (optional): Upload screenshots to the PR automatically

Post the screenshots straight into a PR comment as inline images, instead of asking the user to drag and drop. This drives GitHub's own comment-box uploader, so it produces canonical `…/user-attachments/assets/<uuid>` URLs and works the same on **github.com** and **GitHub Enterprise** (the asset URL host mirrors the PR's host).

**Requirements:**
- A browser session **logged in to the PR's GitHub host**. If it isn't, the page redirects to login — ask the user to log in in the browser, then continue. On Enterprise hosts with 2FA/SSO this is a one-time step; use a persistent browser profile so the session is reused.
- Do **not** use a Personal Access Token for this — GitHub's upload endpoint rejects PATs (`422`). The inline-image upload requires the interactive web session.

**Steps:**

1. `browser_navigate` to the PR (`https://<host>/<owner>/<repo>/pull/<n>`). Confirm you landed on the PR (not a login page) before continuing.
2. For each screenshot, upload it onto the comment form's attachment input with `browser_file_upload`, targeting:

   ```
   form:has(#new_comment_field) file-attachment input[type=file]
   ```

   Use this exact selector — a bare `input[type=file]` matches a different, hidden input that is not wired to the comment box, and the upload silently does nothing.
3. After each upload, read the comment field with `browser_evaluate` (`document.querySelector('#new_comment_field').value`). GitHub first inserts `![Uploading <name>…]()`, then swaps in the final reference, e.g. `<img … src="https://<host>/user-attachments/assets/<uuid>" />`. Poll until a `user-attachments/assets/` URL appears that no longer says `Uploading`, and collect it.
4. Compose a before/after comment from the captured URLs and post it — either submit the comment box, or clear the draft and post a clean comment with `gh pr comment` (the assets are already stored the moment the input fires, so they survive clearing the textarea):

   ```markdown
   | View | Before | After |
   |------|--------|-------|
   | Front page | <img width="450" src="…/assets/AAA"> | <img width="450" src="…/assets/BBB"> |
   ```

   If submitting through the browser UI, click the exact `Comment` button. A broad text match for `Comment` can also match secondary actions such as `Close with comment`.

**Fragility note:** this depends on GitHub's current composer DOM (the `<file-attachment>` custom element). If GitHub restructures the comment box, the selector in step 2 may need updating — it's the one brittle part of this flow.

#### Headless Playwright upload

When screenshots already exist on disk, a coding agent can upload them without opening a visible browser. This uses the same GitHub composer upload flow as above, but drives it through a persistent, authenticated Playwright profile in headless Chrome.

Use this path when:

- The user wants canonical GitHub `user-attachments/assets/` URLs.
- A Playwright-managed browser profile is already logged in to the PR's GitHub host.
- The screenshots are already generated and verified at 2x/device scale.

Do not use this path to bypass login. If the profile lands on the GitHub login page, stop and ask the user to log in through a controlled browser session. Never read cookie values or copy cookies between profiles.

How it works:

- Playwright's `launchPersistentContext(profileDir, ...)` launches Chrome with a real user data directory instead of an empty incognito-style context.
- Chrome stores browser session state in that user data directory: cookies, local storage, session storage, cache, preferences, and other profile data.
- If the user previously logged in to GitHub in that controlled browser profile, headless Chrome can reuse the same browser session later.
- The upload still goes through GitHub's normal web UI. Playwright only automates the file input in the comment composer.
- `gh` is not used for image upload. It is useful after upload to post a clean Markdown comment that references the collected asset URLs.
- `.gitconfig` and Git credential helpers are not used by Chrome for this browser session. They only affect Git and `gh`.
- Browser proxy settings are separate from Git proxy settings. If the GitHub host needs a proxy, pass it to Chrome explicitly, for example with `--proxy-server=...`.

How a profile becomes useful:

1. The agent opens a controlled browser with a persistent profile.
2. The user logs in to the GitHub host once in that browser.
3. Chrome saves the web session in the profile directory.
4. Later headless runs point `PLAYWRIGHT_PROFILE_DIR` at the same profile.
5. If GitHub shows the PR comment box, the session is still valid. If it redirects to login, the profile is not ready.

Safe checks:

- Check whether the PR page has `#new_comment_field` before uploading.
- It is safe to inspect cookie host names or counts to find likely profiles.
- Never print cookie values, session tokens, local storage values, or credential files.
- Do not copy profile directories as an auth workaround. Browser auth can depend on operating-system and browser storage details, and copied profiles may fail or leak sensitive state.

Minimal Node pattern:

```js
const { chromium } = require("playwright");
const fs = require("node:fs");

const prUrl = process.env.GITHUB_PR_URL;
const profileDir = process.env.PLAYWRIGHT_PROFILE_DIR;
const screenshots = process.argv.slice(2);

if (!prUrl || !profileDir || screenshots.length === 0) {
  throw new Error(
    "Usage: GITHUB_PR_URL=<url> PLAYWRIGHT_PROFILE_DIR=<dir> node upload.js screenshots/*.png"
  );
}

(async () => {
  const context = await chromium.launchPersistentContext(profileDir, {
    headless: true,
    channel: "chrome",
    args: process.env.HTTPS_PROXY
      ? [`--proxy-server=${process.env.HTTPS_PROXY}`]
      : [],
  });
  const page = context.pages()[0] || await context.newPage();

  await page.goto(prUrl, {
    waitUntil: "domcontentloaded",
    timeout: 45_000,
  });

  const textarea = page.locator("#new_comment_field");
  if ((await textarea.count()) === 0) {
    throw new Error(
      `GitHub comment box not found. Current URL: ${page.url()}`
    );
  }

  await textarea.scrollIntoViewIfNeeded();
  await textarea.fill("");

  const input = page
    .locator('form:has(#new_comment_field) file-attachment input[type=file]')
    .first();
  await input.waitFor({ state: "attached", timeout: 30_000 });

  const urls = [];
  for (const screenshot of screenshots) {
    if (!fs.existsSync(screenshot)) {
      throw new Error(`Missing screenshot: ${screenshot}`);
    }

    const previousValue = await textarea.inputValue();
    await input.setInputFiles(screenshot);

    await page.waitForFunction(
      (oldValue) => {
        const value =
          document.querySelector("#new_comment_field")?.value || "";
        return (
          value !== oldValue &&
          value.includes("user-attachments/assets/") &&
          !value.includes("Uploading")
        );
      },
      previousValue,
      { timeout: 60_000 }
    );

    const value = await textarea.inputValue();
    const matches = [
      ...value.matchAll(
        /https:\/\/[^)\s"]+\/user-attachments\/assets\/[0-9a-f-]+/g
      ),
    ].map((match) => match[0]);

    for (const url of matches) {
      if (!urls.includes(url)) {
        urls.push(url);
      }
    }
  }

  await textarea.fill("");
  await context.close();
  console.log(JSON.stringify({ urls }, null, 2));
})();
```

Then post a clean PR comment with the collected URLs:

```bash
gh pr comment "$PR_NUMBER" --body-file visual-verification.md
```

The uploaded assets survive clearing the draft textarea because GitHub stores them when the file input upload completes.

## Screenshot directory

Save all screenshots to `./screenshots/` in the repo root. Create the directory if it doesn't exist. This directory should be in `.gitignore` — if it isn't, don't commit the screenshots.

```bash
mkdir -p screenshots
```

## Authentication

Some dev environments require login. Check the repo's CLAUDE.md for auth details. Common patterns:

- **WordPress admin:** Navigate to `/wp-login.php`, fill credentials, then proceed
- **WordPress.com:** Log in at the dev server URL — may require browser cookies from a prior session
- **No auth needed:** Local dev servers like `localhost:3000` often skip auth

If auth fails, tell the user and suggest they log in manually in the browser first.

**Uploading to a PR (Step 6)** needs a browser logged in to the *GitHub host* of the PR (github.com or your Enterprise host) — separate from dev-server auth. Use a persistent browser profile so an Enterprise 2FA/SSO login is a one-time step, and never rely on a Personal Access Token for the image upload (the endpoint rejects it).

## Viewport sizes

| Name | Width | Height | Use when |
|------|-------|--------|----------|
| Desktop | 1280 | 800 | Default for all screenshots |
| Mobile | 390 | 844 | Responsive CSS changes, mobile layouts |
| Tablet | 768 | 1024 | Tablet-specific breakpoints |

Use `browser_resize` to set the viewport before each screenshot.

## Image quality

Capture screenshots at 2x/device-scale quality for every agentic PR screenshot workflow. This is the default because 1x captures make UI text fuzzy after GitHub compression and review-page scaling.

How to apply it:

- Prefer a browser/tool setting such as `deviceScaleFactor: 2`, `scale: "device"`, or equivalent before calling screenshot capture.
- Keep before and after screenshots at the same viewport and device scale.
- Do not fake 2x quality by changing the CSS viewport if that would trigger a different responsive layout.
- If the available browser tool cannot set device scale, capture the most readable PNG it can produce and state the limitation in the summary.
- For custom composite images, generate the source screenshots at 2x first; do not upscale a fuzzy 1x screenshot afterward.

### Troubleshooting 2x captures

Verify the saved image dimensions, not just the browser setting. A 1280x800 viewport captured at 2x should produce a 2560x1600 PNG. Use `sips`, `identify`, or another image metadata tool to confirm the pixel size before uploading evidence.

If the browser reports `devicePixelRatio: 2` but the saved PNG is still 1x, prefer Chrome DevTools Protocol capture from the live authenticated Playwright page when the environment exposes a Playwright code runner. This keeps the logged-in browser session intact and avoids profile-copying problems where authentication can fail even when cookies are present.

```js
const client = await page.context().newCDPSession(page);

await page.setViewportSize({ width: 1280, height: 800 });
await client.send( 'Emulation.setDeviceMetricsOverride', {
	width: 1280,
	height: 800,
	deviceScaleFactor: 2,
	mobile: false,
} );

const capture = await client.send( 'Page.captureScreenshot', {
	format: 'png',
	fromSurface: true,
	captureBeyondViewport: false,
	clip: { x: 0, y: 0, width: 1280, height: 800, scale: 1 },
} );
```

Use `deviceScaleFactor: 2` with `clip.scale: 1`. Combining DPR 2 with `clip.scale: 2` creates a 4x image. If the code runner cannot write files directly, save the returned base64 data through the browser download flow or another local helper; do not paste base64 into PR comments.

Avoid copying browser profiles as an authentication workaround. Browser-level auth can be tied to the live process, so copied profiles may fail with credential errors. Use the existing controlled browser session, or ask the user to finish login in that controlled browser and then continue.

Avoid OS-level screenshot tools as the first fallback. They can hit screen-recording permissions, capture the wrong window, or include unrelated desktop state. Use them only when browser-native capture is unavailable, and state the limitation.

## Tips

- **Don't screenshot everything.** Focus on the views affected by the diff.
- **Consistent state.** Close modals, scroll to the same position, collapse sidebars — keep before/after comparable.
- **Wait for renders.** Use `browser_wait_for` with visible text or `browser_snapshot` to confirm the page is ready before screenshotting.
- **Multiple viewports.** If a CSS change is responsive, capture both desktop and mobile for the same view.
- **PR templates.** Some repos (Gutenberg, WooCommerce) have a before/after table in the PR template. Match that format when suggesting PR text.

## Error handling

| Problem | Action |
|---------|--------|
| Dev server not running | Tell the user which command to run (from repo's CLAUDE.md) |
| Page returns 404/500 | Check the URL, wait for rebuild, retry once |
| Auth required | Prompt user to log in manually, then retry |
| Screenshot is blank/loading | Use `browser_wait_for` with longer timeout, retry |
| Browser not installed | Run `browser_install` to set up Playwright |
| PR upload does nothing / no asset URL | Confirm the browser is logged in to the PR's host; check the Step 6 selector targets the comment-box `file-attachment input` |
