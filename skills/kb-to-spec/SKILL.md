---
name: kb-to-spec
description: Promote a private Markdown plan/note into a shareable spec committed to a GitHub repo. De-privatizes the content, writes a standalone spec with an Authors header, links that spec from the top of the private note, and keeps the two independent (no duplicated content). Use when publishing a plan as a shared design doc, committing KB plans into a project repo, or when the user says "promote this to a spec", "turn this note into a repo spec", or "make this shareable".
---

# kb-to-spec

Turn one of your **private Markdown notes or KB files** into a **shareable spec** committed to a
project's GitHub repo—repeatably, without leaking anything private and without
duplicating content.

## The two-file model

After promotion there are two files, **independent**, no shared text:

| File | Lives in | Holds | Who sees it |
|---|---|---|---|
| **Spec** | the project repo (`<repo>/docs/...`) | the shareable design content, *standalone*—a reader needs nothing else | anyone with repo access |
| **Private note** | your local notes / KB (where it already is) | private-only material—logs, decisions-in-progress, personal meta, internal cross-refs—**plus a link up to the spec** | only you |

**Never duplicate.** If a piece of content is shareable, it lives in the **spec**, and the
private note links to it instead of repeating it. The private note is a thin private layer
*on top of* the spec, not a copy of it.

## Inputs

- **Source:** the private note or KB file to promote (path; ask if not given).
- **Target repo:** your local clone of the target repo (ask if unknown).
- **Spec location:** detect the repo's existing convention—look for an existing
  `docs/**/specs/` dir and a sample spec. **Match what's already there** (path + whether
  specs use YAML frontmatter or a bold `**Authors:**` header). The **Authors** field is the
  de-facto ownership key: every spec lists its real authors, and editing rights follow it.

## Procedure

### 1. Read source and learn the repo's spec convention
Read the private file. In the target repo, find an existing spec and note: where specs
live, the header style (frontmatter vs. inline `**Date/Status/Authors:**`), and the
filename pattern (e.g. `YYYY-MM-DD-<slug>.md`).

### 2. Classify the content
Split the private file into:
- **Shareable** → design, decisions, architecture, rationale, scope, open questions that
  a teammate needs.
- **Private-only** → keep in the note: personal meta ("my lane", who-owns-what framing),
  internal cross-references that only resolve in your local file system (e.g. links to
  other private notes), log entries, draft messages, anything that only makes sense
  inside your own environment.

### 3. Build the spec (de-privatized and standalone)
From the shareable content, write a spec that reads end-to-end as a shared design doc:
- **Strip every private artifact:** local paths (any absolute path like `/Users/<name>/`,
  home-directory paths starting with `~/`, or project-relative paths that only resolve
  inside your private notes tree), links or line-refs to private notes, and personal
  framing. Also strip any directory names that are part of your private organizational
  structure—if you keep notes under folders like `Notes/`, `Private/`, `Archive/`, or
  similar, those paths must not appear in the spec. Replace a needed reference with a
  link the reader can actually open (the repo, a Linear issue, a project management tool,
  a public doc) or describe it inline.
- **Add the header in the repo's style**, with an **Authors** field listing the spec's
  real authors so the ownership convention applies here too.
- Rewrite any "I will / I own" framing into neutral shared language.

### 4. Privacy gate (mandatory before writing/committing)
Scan the drafted spec for absolute paths (`/Users/`, `/home/`), home-directory paths
(`~/`), and Markdown links ending `.md)` that point at private local files. Also scan for
any directory names from your own private notes tree that you identified in step 2.
**If any appear, fix them before continuing.** Refuse to write a spec that still
contains them—leaking local paths into a shared repo is a hard boundary.

To identify your private directory patterns, look at the source note's own location and
sibling folders. If the user has not told you which folder names are private, ask them to
list any top-level dirs in their notes tree that should never appear in shared content.
A common pattern: notes live under a home directory like `~/Notes/` or `~/Obsidian/`,
with sub-folders like `Projects/`, `People/`, `Archive/`—all of those would be private.

### 5. Write the spec
Write to the detected path/filename in the repo. Do **not** auto-commit or push (see step 7).

### 6. Rewrite the private note
Convert the source file into the private companion:
- **Add a spec link at the very top**—a callout pointing at the committed spec (the repo
  URL once pushed; the local clone path is fine too since this file is private). Example:
  `> 📋 **Shared spec:** [<title>](<repo-url-or-path>)—design content lives there; this note is private-only.`
- **Remove the shareable content** now living in the spec (no duplication).
- **Keep** the private-only material from step 2, and leave room for ongoing private
  notes/logs.

### 7. Stop before commit—hand off to you
Do **not** commit or push to a shared repo automatically. Instead:
- Show the new spec and a `git status`/`git diff` of the repo.
- Surface the exact commands (branch or trunk per the repo's actual convention—your
  call), e.g. `git -C <repo> add <spec> && git -C <repo> commit -m "..."`.
- Let the user review and run the commit. Never `git push` or merge on their behalf.

## Ongoing maintenance (repeat use)

- Once promoted, **shareable edits go in the spec**; **private notes accrue in the local
  note.** Don't migrate content back and forth.
- On a re-run against an already-promoted file, verify no shareable content has crept back
  into the private note (and no private content has leaked into the spec). Reconcile by
  moving each to its correct home—still no duplication.

## Output

Report: the spec path written, the private note's new top-link, what was stripped in the
privacy pass, and the ready-to-run commit command for the user.
