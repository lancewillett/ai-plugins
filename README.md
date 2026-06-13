# lance-skills

Public skills and plugins for Claude Code and Codex. General-purpose—nothing environment-specific.

## Install

### Claude Code

Add this marketplace once:

```
/plugin marketplace add https://github.com/lancewillett/skills.git
```

Then install any plugin by name:

```
/plugin install kb-to-spec@lance-skills
```

### Codex

Add this marketplace once:

```
codex plugin marketplace add https://github.com/lancewillett/skills.git
```

Then install any plugin by name:

```
codex plugin install kb-to-spec@lance-skills
```

## Skills

### kb-to-spec

Promote a private Markdown note into a shareable spec committed to a GitHub repo.

It de-privatizes the content, writes a standalone spec with an Authors header, links back from the private note, and keeps the two files independent—no duplicated content.

Use it when publishing a plan as a shared design doc, committing notes into a project repo, or when you say "promote this to a spec", "turn this note into a repo spec", or "make this shareable".

## Repo layout

```
.claude-plugin/marketplace.json      — Claude Code marketplace manifest
.agents/plugins/marketplace.json     — Codex marketplace manifest
skills/<name>/SKILL.md               — generalized skill source
plugins/<name>/
  .claude-plugin/plugin.json         — Claude Code plugin manifest
  .codex-plugin/plugin.json          — Codex plugin manifest
  skills/<name>/SKILL.md             — packaged skill (copy of source)
```

## Contributing

This repo is for personal use, but pull requests that improve or generalize existing skills are welcome. New skills should be general-purpose—nothing environment-specific.

## License

MIT: see [LICENSE](./LICENSE).
