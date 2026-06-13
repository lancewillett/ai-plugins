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

### claude-cleanup

Audit and clean up your Claude Code configuration. It checks skills, hooks, settings, plugins, configs, commands, and stale data for broken references, outdated paths, version drift, and orphaned files, then fixes them interactively (or previews with `--dry-run`). Use it for periodic maintenance, after a folder reorganization, or when you say "clean up my Claude config" or "audit my skills and plugins".

## Contributing

This repo is for personal use, but pull requests that improve or generalize existing skills are welcome. New skills should be general-purpose and not private or environment-specific.

## License

MIT: see [LICENSE](./LICENSE).
