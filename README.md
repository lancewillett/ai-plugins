# lance-skills

Lance Willett's public Claude Code skills marketplace. General-purpose skills and plugins for use with [Claude Code](https://claude.ai/claude-code).

## Install

Add this marketplace to Claude Code once:

```
/plugin marketplace add https://github.com/lancewillett/skills.git
```

Then install any plugin by name:

```
/plugin install kb-to-spec@lance-skills
```

## Skills

### kb-to-spec

Promote a private Markdown note into a shareable spec committed to a GitHub repo.

It de-privatizes the content, writes a standalone spec with an Authors header, links back from the private note, and keeps the two files independent — no duplicated content.

Use it when publishing a plan as a shared design doc, committing notes into a project repo, or when you say "promote this to a spec", "turn this note into a repo spec", or "make this shareable".

## Repo layout

```
.claude-plugin/marketplace.json   — marketplace manifest
skills/<name>/SKILL.md            — generalized skill source
plugins/<name>/
  .claude-plugin/plugin.json      — plugin manifest
  skills/<name>/SKILL.md          — packaged skill (copy of source)
```

## Contributing

This repo is primarily for personal use, but pull requests that improve or generalize existing skills are welcome. New skills should be general-purpose — nothing environment-specific.

## License

MIT — see [LICENSE](./LICENSE).
