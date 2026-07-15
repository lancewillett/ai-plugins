# Lance's AI plugins

Public skills, commands, and scripts wrapped into a simple plugin marketplace that works with both Claude Code and Codex.

## Install

### Claude Code

Add this marketplace once:

```
/plugin marketplace add https://github.com/lancewillett/ai-plugins.git
```

Then install any plugin by name:

```
/plugin install kb-to-spec@ai-plugins
```

### Codex

Add this marketplace once:

```
codex plugin marketplace add https://github.com/lancewillett/ai-plugins.git
```

Then install any plugin by name:

```
codex plugin install kb-to-spec@ai-plugins
```

## Skills

### kb-to-spec

Promote a private Markdown note into a shareable spec committed to a GitHub repo. It de-privatizes the content, writes a standalone spec with an Authors header, links back from the private note, and keeps the two files independent, with no duplicated content. Use it when publishing a plan as a shared design doc, committing notes into a project repo, or when you say "promote this to a spec", "turn this note into a repo spec", or "make this shareable".

### js-perf-audit

Audit any JS-heavy codebase for performance issues. It checks bundle weight, dependency hygiene, code splitting, rendering architecture, runtime re-render patterns, and performance infrastructure, then writes a findings report with severity ratings and prioritized recommendations. Use it when you want to assess or improve a JavaScript app's performance, or when you say "audit this codebase for performance", "check our bundle size", or "why is this app slow".

### visual-screenshots

Capture before/after screenshots for PRs with visual UI changes using Playwright. It reads the repo's dev-server setup, captures matched before/after shots at the right viewports, and can upload them straight into the PR comment as inline images (works on github.com and GitHub Enterprise). Use it when a PR changes CSS, components, layouts, or themes, or when you say "screenshot this change" or "add before/after screenshots to the PR". Requires the Playwright MCP server.

### claude-cleanup

Audit and clean up your Claude Code configuration. It checks skills, hooks, settings, plugins, configs, commands, and stale data for broken references, outdated paths, version drift, and orphaned files, then fixes them interactively (or previews with `--dry-run`). Use it for periodic maintenance, after a folder reorganization, or when you say "clean up my Claude config" or "audit my skills and plugins".

### authed-browser-runner

Run repeatable headless-browser checks against a site behind a login wall — HTTP Basic Auth, SSO, or a session cookie — by authenticating once and attaching over the Chrome DevTools Protocol for every run after. It documents the auth-once session model, a reference Playwright runner (start a session, attach and drive, 2x screenshots, scoped teardown), and the collision and auth-capture pitfalls that waste the most time. Use it when a page needs a login your script can't drive and you'll check it more than once, or when you say "test this authed page with Playwright" or "set up a reusable headless browser session".

## Contributing

This repo is for personal use, but pull requests that improve or generalize existing skills are welcome. New skills should be general-purpose and not private or environment-specific.

## License

MIT: see [LICENSE](./LICENSE).
