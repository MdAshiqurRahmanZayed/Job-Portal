# Design

## Context

See proposal.md - Why. `IS_PSQL` and `USE_S3` are currently two
**independent** env-var toggles (`jobPortal/settings.py:95,145`) — a
deployment could in principle run Postgres without S3, or vice versa.
A naive `development.py`/`production.py` split that picks one file
based on a single flag would collapse that independence.

## Goals / Non-Goals

**Goals:**
- Reorganize settings into a package without changing what any given
  combination of `IS_PSQL`/`USE_S3`/other env vars resolves to.
- Keep the two toggles independent, exactly as today.

**Non-Goals:**
- Introducing a new `DJANGO_ENV`/`ENVIRONMENT` var to pick a settings
  module — that would be a behavior change (a new required/optional
  env var), not a pure reorganization.
- Changing any default value.

## Decisions

### D1: Keep `IS_PSQL` and `USE_S3` as independent conditionals inside `base.py`, not as file-selection switches
Rather than `development.py` vs `production.py` selecting an entire
settings profile, `base.py` keeps the same `if IS_PSQL: ... else: ...`
and `if USE_S3: ... else: ...` blocks it has today — just organized
under clearly commented sections. This preserves the exact today's
behavior (independent toggles) instead of forcing them into a single
dev/prod axis they were never designed around.

Given this, the proposal's `development.py`/`production.py` split (one
file per environment) does not fit this codebase's actual toggle
structure. Revised plan: **`jobPortal/settings/base.py`** holds
everything, unchanged in behavior from today's single file, just
moved into a package for future extensibility (e.g. a `test.py`
override later, if ever needed) — `jobPortal/settings/__init__.py`
simply does `from .base import *`. No `development.py`/`production.py`
files are created in this pass, since the env vars don't actually
divide along that line.

Alternative considered: force a single `DJANGO_ENV` var and reorganize
around it. Rejected — that changes deployment configuration (a new
required decision at deploy time) for a change proposed as pure
reorganization; if the project later wants a true dev/prod switch,
that's a separate, deliberate proposal.

## Risks / Trade-offs

- **This revises the proposal's own premise** (real dev/prod files →
  a single reorganized `base.py`). → Flagged here explicitly rather
  than silently implementing something different from what was
  proposed; if a real dev/prod split is still wanted despite the
  independent-toggles reality, that needs a follow-up conversation
  about introducing `DJANGO_ENV`, not this change.
- **`DJANGO_SETTINGS_MODULE`** currently likely reads
  `"jobPortal.settings"` — must confirm this still resolves once
  `settings.py` becomes `settings/__init__.py` (it does, per Python's
  package-import rules, but verify via `manage.py check` rather than
  assuming).
- **`BASE_DIR` computation breaks silently** (found during apply, not
  anticipated here): `BASE_DIR = Path(__file__).resolve().parent.parent`
  assumed `settings.py` sits directly under the project package
  (`jobPortal/settings.py` → `.parent.parent` = repo root). Moving it
  to `jobPortal/settings/base.py` adds a directory level, so the same
  expression resolves to `jobPortal/` instead of the repo root —
  `manage.py check` reported a stale `STATICFILES_DIRS` warning that
  caught this immediately. Fix: `.parent.parent.parent`. This is
  exactly the kind of subtle breakage this design's own verification
  steps (task 1.1/1.2) exist to catch — confirms the "verify, don't
  assume" approach was warranted.

## Migration Plan

1. Create `jobPortal/settings/` package; move all content from
   `settings.py` into `settings/base.py` unchanged.
2. `settings/__init__.py`: `from .base import *`.
3. Delete the old `jobPortal/settings.py`.
4. Run `manage.py check`, `manage.py test`, and `docker compose up`
   to confirm settings still resolve correctly in both the `IS_PSQL`
   and non-`IS_PSQL` cases.

Rollback: revert the commit; no data/schema change.

## Open Questions

None — the toggle-independence finding is resolved above (D1), not
deferred.
