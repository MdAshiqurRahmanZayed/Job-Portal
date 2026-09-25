---
name: git-conventions
description: >
  Generate Conventional Commits messages, branch names, PR titles, and PR
  descriptions for this repository. Works with or without a ticket/task key —
  when no ticket system applies, use plain `type(scope): description` instead
  of forcing an ID. Trigger on "commit message", "write a commit", "branch
  name", "PR description", "PR title", "conventional commits", "what should I
  commit this as", "help me with my PR", or when the user pastes a diff and
  asks what to write. Also trigger on "review/fix this commit message".
---

# Git Conventions

Generate commit messages, branch names, PR titles, and PR descriptions that
follow Conventional Commits. Every output must be usable as-is — no
placeholders left for the developer to fill in unless information genuinely
cannot be inferred from the diff/context given.

**Ticket keys are optional.** If the user's task tracker is not being used, or
no ticket exists yet, do not invent one and do not leave a `<ticket-id>`
placeholder — just write `type(scope): description` and skip ticket footers.
If this repo's own `CLAUDE.md` or `CONTRIBUTING.md` documents a mandatory
ticket-key format (e.g. a project prefix in branch names/PR titles), follow
that when a ticket key is available or given; otherwise fall back to the
plain format below.

---

## 1. Commit Messages

### Format

```
<type>(<scope>): <short description>

<optional body>

<optional footer(s)>
```

### Rules

1. **Type** — exactly one of these (nothing else is valid):

   | Type       | Use for |
   |------------|---------|
   | `feat`     | New feature visible to a user, API consumer, or another developer |
   | `fix`      | Bug fix |
   | `refactor` | Internal restructuring — no new features, no bug fixes |
   | `perf`     | Performance improvement. State the measured improvement in the body |
   | `test`     | Adding or updating tests only. No production code changes |
   | `docs`     | Documentation only — README, ADRs, code comments, runbooks |
   | `build`    | Build system, dependencies, or packaging changes |
   | `ci`       | CI/CD pipelines, deployment scripts |
   | `chore`    | Maintenance that doesn't fit above. Use sparingly |

   **Forbidden types:** `misc`, `update`, `wip`, `changes`, or anything not in
   the table above.

2. **Scope** — optional but strongly preferred. Name the module/package/app
   being changed. In this repo, prefer the Django app name (e.g. `accounts`,
   `main`, `jobPortal`), or a cross-cutting area like `docker`, `ci`, `docs`
   when the change isn't app-specific.

3. **Description** (subject line after the colon):
   - Imperative mood: "add", not "added" or "adds"
   - Think: "If applied, this commit will ___"
   - Starts lowercase, no trailing period
   - Total line (type + scope + colon + space + description) ≤ 72 characters
   - Describes **what the change does**, not which files were touched

4. **Body** (blank line after the subject):
   - Required for any non-trivial change
   - Explains **why** the change was made — problem, approach chosen,
     alternatives considered, side effects, migration steps
   - Wrap lines at 72 characters

5. **Breaking changes**:
   - Inline: `feat(auth)!: replace token format`
   - Or footer: `BREAKING CHANGE: token storage moved from cookie to header`
   - Prefer the footer form when migration steps are non-trivial

6. **Footers** — only include the ones that apply:
   ```
   Closes <ticket-id>          (only if a ticket exists)
   Refs <ticket-id>, <ticket-id>
   Reviewed-by: Name
   Co-authored-by: Name <email>
   BREAKING CHANGE: description of what breaks
   ```
   Omit ticket footers entirely when there's no ticket — don't fabricate one.

### Forbidden commit messages

Never produce: `fix`, `wip`, `updates`, `asdf`, `merge branch '...'`,
`fix bug`, `review changes`, or any commit with no type prefix.

### Examples

**No ticket, straightforward fix:**
```
fix(main): correct off-by-one in job listing pagination
```

**No ticket, feature with body:**
```
feat(accounts): add developer-wise summary to hour report

Aggregates logged hours per developer within the existing report
query instead of a separate pass, so the summary stays in sync
with the detail rows.
```

**With a ticket:**
```
fix(accounts): block negative notice period past joining date

Approval wizards allowed a computed notice period below zero when
the joining date preceded the last working day. Clamp at zero and
surface a validation error instead.

Closes SE360-1594
```

**Breaking change:**
```
feat(api)!: change pagination from offset to cursor-based

All list endpoints now require a `cursor` parameter instead of
`page`/`page_size`. Offset-based pagination is removed.

BREAKING CHANGE: clients using offset pagination must migrate to
cursor-based pagination.
```

---

## 2. Branch Names

### Format

```
<type>/<scope>-<short-slug>
```

Use `<type>/<scope>_<short-slug>` (underscore) only if this repo's own
`CLAUDE.md` mandates that style with a ticket key baked in — check for a
project-specific convention before defaulting to hyphens.

### Examples

```
feat/accounts-developer-hour-summary
fix/main-job-listing-pagination-off-by-one
refactor/jobPortal-api-key-lookup
chore/upgrade-django
```

### Forbidden branch names

- Ticket number only: `SE360-1594`
- Person's name: `zayed-stuff`
- Unstructured: `new-auth-flow-v2-final`

---

## 3. PR Titles

Same Conventional Commits format as the commit subject.

- Single-commit PR: title and commit subject should match.
- Squash-merged PR: title becomes the final commit subject — get it right.

### Forbidden PR titles

- Restating the branch name as a sentence
- Only a ticket number
- Vague: `Update X` or `Fix X` without saying what

---

## 4. PR Description

Five-section template. Trivial PRs (typo fixes, dependency bumps) may
collapse to a single sentence under **What**.

```markdown
## What
One paragraph: what this PR changes, written for a reviewer who
hasn't seen any prior discussion.

## Why
One paragraph: the problem this solves or the goal it advances.
Link a ticket/issue/discussion if one exists — otherwise state the
motivation directly, don't force a reference.

## How
Bullet list of the technical approach. Note any non-obvious choices,
deviations from convention, or trade-offs accepted.

## Verification
How to confirm this works: test commands run, manual steps taken,
screenshots, before/after behavior.

## Risks & Follow-up
Known limitations, deferred work, anything reviewer/maintainer
should watch for after merge.
```

Add an `AI involvement: none / drafting / extensive` footer line only if
this project tracks that; otherwise omit it.

---

## 5. How to Use This Skill

**Diff or change description given:**
1. Identify the correct type from the change content.
2. Infer scope from the modules/files touched.
3. Write the subject in imperative mood, ≤72 chars.
4. Write a body explaining why (skip only for truly trivial changes).
5. Add footers only for what actually applies (ticket, breaking change,
   co-author) — never invent a ticket ID.

**PR description requested:**
1. Ask for (or infer from context) the commit(s) in the PR.
2. Fill in all five sections.
3. Flag any section where you're guessing and tell the user to verify.

**Review/fix existing commits:**
1. Identify what's wrong (missing type, vague description, no body, etc).
2. Provide the corrected version.
3. Briefly explain what was fixed and why.

**Output format:**
- Always output the commit message / branch name / PR description in a
  fenced code block so it's easy to copy.
- Number multiple commits when generating a series.
- For PR descriptions, use the markdown template directly.
