# claude-cleanup

Audit and clean up your Claude Code configuration. Run periodically to keep your setup clean and consistent.

## What it checks

1. **Skills** — broken references, outdated paths, duplicates
2. **Hooks & settings** — missing scripts, redundant permissions
3. **CLAUDE.md files** — outdated paths, misplaced files
4. **Plugins** — version drift, cache integrity
5. **Configs** — path consistency, stale project directories
6. **Commands** — broken references, dead links

## Usage

```
/claude-cleanup              # Full audit with interactive fixes
/claude-cleanup --dry-run    # Preview changes without applying
/claude-cleanup --step=3     # Run only step 3 (CLAUDE.md audit)
```

## When to run

- Monthly maintenance
- After major folder reorganizations
- After installing/removing plugins
- When things feel "off"

## Install

```
/plugin marketplace add https://github.com/lancewillett/ai-plugins.git
/plugin install claude-cleanup@ai-plugins
```
