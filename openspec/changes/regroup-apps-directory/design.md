# Design

## Context

See proposal.md - Why. Django's `AppConfig` default `label` is derived
from the last segment of the app's dotted path
(`django.apps.config.AppConfig._path_from_module` /
`AppConfig.create`), so `apps.accounts` still gets label `accounts`
without any explicit `AppConfig.label` override — this is the load-
bearing assumption behind "migrations are unaffected," and must be
verified, not just asserted.

## Goals / Non-Goals

**Goals:**
- Move both apps under `apps/` with zero behavior change: same app
  labels, same migration history, same URLs, same templates.

**Non-Goals:**
- Renaming any app (`accounts`/`main` stay `accounts`/`main`).
- Combining with any other phase's changes in the same commit — this
  should be the last phase applied, once 1-4 are stable, specifically
  because it's the one most likely to produce merge conflicts with
  everything else if done concurrently (every file in both apps
  moves).

## Decisions

### D1: No custom `AppConfig.label` override needed
Rely on Django's default label derivation (last dotted-path segment)
rather than adding an explicit `label = "accounts"` to
`AccountsConfig`/`MainConfig`. Simpler, and the default behavior
already gives the exact same label as today.

Alternative considered: add explicit labels defensively. Rejected —
adds a config line whose only job is to reproduce default behavior;
if that default behavior turns out wrong, the fix task (2.1 below) is
exactly to add it, but do that reactively based on what `manage.py
makemigrations --check` reports, not preemptively.

### D2: Do this phase in complete isolation, not alongside other phases
Every file under `accounts/`/`main/` moves. Any other phase (services
extraction, settings split, API versioning) touching those same files
concurrently on a different branch will conflict hard on rebase. This
phase should only start once Phases 1-4 are merged.

## Risks / Trade-offs

- **Migration history assumption (D1) turns out wrong** → Mitigation:
  task 2.1 runs `manage.py makemigrations --check --dry-run`
  immediately after the move, before touching anything else; if it
  detects a change, stop and add explicit `AppConfig.label` overrides
  rather than proceeding.
- **Large mechanical diff makes review harder** → Mitigation: keep the
  directory move and the import-statement updates as separate commits
  within the same PR (move first, then fix imports) so reviewers can
  verify the move step is a pure `git mv` with no content changes.
- **Highest merge-conflict risk of all 5 phases** (per D2) → Mitigation:
  sequence it last.

## Migration Plan

1. `git mv accounts apps/accounts`, `git mv main apps/main` (pure
   moves, no content edits in this commit).
2. Update `INSTALLED_APPS` in settings.
3. Update all cross-app imports (11 files found at proposal time,
   re-grep at apply time).
4. Update `jobPortal/urls.py`'s two `include(...)` calls.
5. Run `manage.py makemigrations --check --dry-run` — must report no
   changes. If it does, stop and add explicit `AppConfig.label`
   overrides (D1's fallback), then re-check.
6. Run the full test suite, `ruff check`/`format`, and
   `docker compose up --build`.

Rollback: revert the commit(s); no data/schema change (verified by
step 5, not just assumed).

## Open Questions

None — the load-bearing assumption (D1) has a concrete verification
step (task 2.1 / migration plan step 5), not left unresolved.
