# Proposal

## Why

`accounts/` and `main/` sit at the repo root instead of under a
common `apps/` directory. This is purely cosmetic — Django doesn't
require it, and the project's default app label (`accounts`, `main`)
stays identical either way (Django derives the default app label from
the last segment of the dotted path, so `apps.accounts` still labels
as `accounts`). **This is the lowest-value, highest-risk item in the
refactor roadmap** and should be done last, if ever — every other
phase (services extraction, Sentry, settings split, API versioning)
delivers real risk reduction or observability; this one delivers
directory tidiness for a real risk of import-path mistakes across
the whole codebase.

## What Changes

- Move `accounts/` → `apps/accounts/`, `main/` → `apps/main/`.
- Update `INSTALLED_APPS` (`"main"`→`"apps.main"`,
  `"accounts"`→`"apps.accounts"`).
- Update all cross-app imports (11 files found: `accounts/views.py`,
  `accounts/tests/*.py` (3 files), `main/context_processors.py`,
  `main/models.py`, `main/views.py`, `main/tests/*.py` (3 files)) from
  `from accounts...`/`from main...` to
  `from apps.accounts...`/`from apps.main...`.
- Update `jobPortal/urls.py`'s two `include("main.urls")`/
  `include("accounts.urls")` calls.
- Verify migrations are unaffected (they reference the app **label**,
  `accounts`/`main`, which does not change — confirmed via Django's
  default-label behavior, but this is exactly the kind of assumption
  this change must verify with a real migration-check run, not just
  reasoning about it).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
None — pure directory/import reorganization, no behavior change.
`skip_specs: true` is set in `.openspec.yaml`.

## Impact

- Every `.py` file under `accounts/`/`main/` moves path.
- 11 files need import statement updates (found via grep; re-verify
  at apply time since other phases may add more cross-app imports
  before this one ships).
- `jobPortal/settings.py` (or `settings/base.py` if Phase 3 shipped
  first), `jobPortal/urls.py`.
- `AUTH_USER_MODEL = "accounts.Account"` stays unchanged (app label,
  not path).
- Full test suite + `manage.py makemigrations --check --dry-run` (to
  confirm Django doesn't think anything changed) are the
  behavior-preservation check.
