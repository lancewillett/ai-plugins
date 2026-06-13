---
name: claude-cleanup
description: Audit and clean up Claude Code configuration. Checks skills, hooks, plugins, configs, commands, and stale data for issues and fixes them.
argument-hint: "[--step name] [--dry-run]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Claude Code Configuration Cleanup

Comprehensive audit and cleanup of Claude Code configuration. Run periodically (monthly recommended) to keep your setup clean and consistent.

## Arguments

- No argument: Run full 6-step audit with interactive fixes
- `--dry-run`: Report issues without making changes
- `--step=N`: Run only step N (1-6)

## Workflow

### Step 1: Skill Audit

**Goal:** Find broken references, outdated paths, and duplicates in custom skills.

**Locations to scan:**
- `~/.claude/skills/` (global)
- `~/Source/.claude/skills/` (Source-level)
- Project-level `.claude/skills/` directories

**Checks:**
1. **Broken skill references:** Grep for `/skill-name` patterns and verify referenced skills exist
2. **Broken command references:** Grep for `/command-name` patterns and verify commands exist
3. **Outdated paths:** Search for old folder names that have been renamed
4. **Duplicate skills:** Compare skill names across locations

**Report format:**
```
Step 1: Skill Audit
───────────────────
Locations scanned: 3
Skills found: 12

Issues:
  ~/.claude/skills/example/SKILL.md
    ⚠ References /missing-skill (line 45) - skill not found
    ⚠ Path "old-folder/" should be "new-folder/"

Actions:
  1. Remove reference to /missing-skill or create it
  2. Update path from old-folder/ to new-folder/
```

**If not --dry-run:** Offer to fix each issue interactively.

---

### Step 2: Hooks & Settings Audit

**Goal:** Verify hooks work and clean up stale permissions.

**Files to check:**
- `~/.claude/settings.json`
- `~/.claude/settings.local.json`
- `~/.claude/hooks/` directory

**Checks:**
1. **Hook scripts exist:** Verify each script referenced in settings.json exists
2. **Orphaned scripts:** Find scripts in hooks/ not referenced in settings
3. **Redundant permissions:** Flag bash commands that have dedicated tools:
   - `Bash(cat:*)` → use Read tool
   - `Bash(find:*)` → use Glob tool
   - `Bash(grep:*)` → use Grep tool
4. **One-off permissions:** Flag overly specific permissions (debugging artifacts)

**Report format:**
```
Step 2: Hooks & Settings Audit
──────────────────────────────
Hooks configured: 2 (SessionStart, SessionEnd)
Hook scripts: 5 in ~/.claude/hooks/
Permissions: 37 entries

Issues:
  ⚠ Orphaned script: ~/.claude/hooks/old-script.sh (not in settings)
  ⚠ Redundant: Bash(cat:*) - prefer Read tool
  ⚠ One-off: Bash(/specific/path/to/thing) - consider removing

Actions:
  1. Delete orphaned script or add to settings
  2. Remove redundant bash permissions
```

---

### Step 3: CLAUDE.md Files Audit

**Goal:** Find outdated paths and misplaced instruction files.

**Locations to scan:**
- `~/.claude/CLAUDE.md` (global)
- Project-level CLAUDE.md files
- Archived CLAUDE.md files

**Checks:**
1. **Outdated paths:** Search for renamed folder references
2. **Archived files:** Check if CLAUDE.md in archive folders have stale content
3. **Scope appropriateness:** Verify files are at the right level (global vs project)

**Report format:**
```
Step 3: CLAUDE.md Files Audit
─────────────────────────────
Files found: 23

Issues:
  archive/2026-01/CLAUDE.md
    ⚠ References "old-folder/" - folder renamed to "new-folder/"
    ⚠ In archive with outdated content - recommend deletion

Actions:
  1. Delete archived CLAUDE.md with outdated paths
```

---

### Step 4: Plugin Health Check

**Goal:** Verify installed plugins are current and working.

**Files to check:**
- `~/.claude/settings.json` (enabledPlugins)
- `~/.claude/plugins/installed_plugins.json`
- `~/.claude/plugins/marketplaces/*/`

**Checks:**
1. **Version comparison:** Compare installed version vs marketplace version
2. **Cache integrity:** Verify install paths exist
3. **Marketplace sync:** Check if local marketplace is behind remote
4. **Orphaned plugins:** Find enabled plugins missing from installed_plugins.json

**Report format:**
```
Step 4: Plugin Health Check
───────────────────────────
Enabled plugins: 3
Marketplaces: 3

Plugin Status:
  example-plugin   0.2.5  ✓ current
  another-plugin   0.6.0  ⚠ update available (0.6.1)
  third-plugin     1.1.0  ✓ current

Marketplace Status:
  example-marketplace  ✓ up to date
  other-marketplace    ⚠ 5 commits behind

Actions:
  1. Update another-plugin: claude plugins update another-plugin
  2. Update marketplace: cd ~/.claude/plugins/marketplaces/other-marketplace && git pull
```

---

### Step 5: Config Consistency

**Goal:** Ensure paths in config files match current folder structure.

**Files to check:**
- Per-plugin config files, e.g. `~/.claude/<plugin>.json` (if any exist)
- Custom config files with paths
- Skill files with hardcoded paths

**Path patterns to search:**
Search for old folder names that have been renamed. If you reorganized your
notes or project layout, list the old → new folder pairs and search for the
old names, e.g.:
- `old-notes-folder/` (may now be `new-notes-folder/`)
- `old-archive-folder/` (may now be `new-archive-folder/`)

**Also check:**
- Stale project directories in `~/.claude/projects/` for renamed folders

**Report format:**
```
Step 5: Config Consistency
──────────────────────────
Configs checked: 3
Project directories: 41

Issues:
  ⚠ Stale project dir: ~/.claude/projects/<encoded-old-path> (1.1MB)
    Original folder renamed, safe to delete

Actions:
  1. Delete stale project directories
```

---

### Step 6: Prune Old Commands

**Goal:** Review custom slash commands for broken references and unused commands.

**Locations to scan:**
- `~/.claude/commands/` (global)
- Project-level `.claude/commands/` directories

**Checks:**
1. **Broken references:** Grep "Related" sections for non-existent commands
2. **Broken skill references:** Verify `/skill-name` references exist
3. **Outdated paths:** Search for renamed folder references

**Report format:**
```
Step 6: Prune Old Commands
──────────────────────────
Commands found: 8

Issues:
  example-command.md
    ⚠ References /old-command (line 148) - command not found
    → Suggest: /current-command does similar work

Actions:
  1. Update reference from /old-command to /current-command
```

---

## Summary Report

After all steps, display summary:

```
Claude Code Cleanup Complete
════════════════════════════

Step                    Status    Issues Fixed
────────────────────────────────────────────
1. Skills               ✓         2 references fixed
2. Hooks & Settings     ✓         1 script deleted, 16 permissions removed
3. CLAUDE.md Files      ✓         1 file deleted
4. Plugin Health        ✓         No action needed
5. Config Consistency   ✓         3 stale dirs deleted (5MB)
6. Commands             ✓         3 references fixed

Space recovered: ~5MB
```

## Log Output

After completion, offer to save detailed log to `~/.claude/docs/`:

```
Save cleanup log to ~/.claude/docs/cleanup-log-YYYY-MM-DD.md? (y/n)
```

## Error Handling

| Error | Action |
|-------|--------|
| Permission denied | Skip file, note in report |
| Config parse error | Warn and continue |
| Missing directory | Skip check for that location |
| Git fetch failed | Report marketplace as "unknown status" |

## Tips

- Run monthly to catch config drift
- Run after major folder reorganizations
- Run after installing/removing plugins
- Use `--dry-run` first to preview changes
