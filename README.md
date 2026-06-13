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

## Contributing

This repo is for personal use, but pull requests that improve or generalize existing skills are welcome. New skills should be general-purpose and not private or environment-specific.

## License

MIT: see [LICENSE](./LICENSE).
