# AGENTS.md

Public, general-purpose AI workflow assets for Claude Code and Codex: plugins, standalone skills, and slash commands. Nothing environment-specific.

## Repo layout

- `.claude-plugin/marketplace.json`: Claude Code marketplace manifest listing installable plugins.
- `.agents/plugins/marketplace.json`: Codex marketplace manifest (same plugins, Codex format).
- `plugins/<name>/`: a packaged plugin with `.claude-plugin/plugin.json` (Claude Code), `.codex-plugin/plugin.json` (Codex), and a `skills/<name>/SKILL.md` copy.
- `skills/<name>/SKILL.md`: the generalized skill source that packaged plugins copy from.

Slash commands, when a plugin ships them, live under `plugins/<name>/commands/`.

## Working conventions

- Keep edits small and practical. This is a personal automation repo, not a product framework.
- Update `README.md` when adding, removing, or renaming a skill, plugin, command, or doc.
- Prefer editing existing skill instructions over adding scripts unless repeated execution genuinely needs code.
- A packaged plugin's `skills/<name>/SKILL.md` is a copy of the source. Keep the two in sync when you change either.
- Keep both marketplace manifests (`.claude-plugin/` and `.agents/plugins/`) consistent when adding or renaming a plugin.

## Safety notes

- Everything here is public. Keep it general-purpose: nothing tied to a specific employer, account, host, or private system.
- Never commit secrets, credentials, tokens, or API keys. Check for presence or names only; never read or paste a secret value.
- Never commit local file paths, machine-specific noise, or generated state.
- Leave `.DS_Store` and unrelated local files alone unless asked to clean them up.
