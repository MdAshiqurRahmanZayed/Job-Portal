# Design

## Context

See proposal.md - Why. Relevant current state:

- `AUTH_USER_MODEL = "accounts.Account"` — a custom user model with a
  custom `MyAccountManager`.
- `DATABASES` uses Postgres only when `IS_PSQL=true`; otherwise it
  falls back to sqlite (`jobPortal/settings.py`). Django's test runner
  always creates a fresh test database regardless of engine, so tests
  run against sqlite in CI/local dev without needing Postgres running.
- `main/urls.py` / `main/views.py`: job and application views are
  function-based, decorated with `@login_required(login_url="login")`;
  ownership checks (e.g. only a job's creator can update/delete it) are
  implemented inline in the view bodies — this design does not assume
  they are already correct; tests will confirm actual behavior first.
- `.github/workflows/ruff-check.yml` is the only existing CI workflow
  relevant here (lint-only, no test execution).

## Goals / Non-Goals

**Goals:**
- Cover every view with real branching logic in `accounts` and `main`:
  registration/login/logout, profile/education/mobile-number
  onboarding, job CRUD + filtering + ownership permissions, application
  submission + listing + employer-side applicant view + permission
  checks, and the two chat API endpoints — using Django's built-in
  `TestCase`.
- Wire test execution into CI so it runs on every PR.

**Non-Goals:**
- Adding a new test-data/factory library (e.g. `factory_boy`) — the
  fixture needs here are small enough for plain `Model.objects.create`
  helpers in a shared test base class; revisit only if test setup
  becomes unwieldy in a later change.
- Coverage percentage tooling/thresholds (`coverage.py`, badges) — can
  be a follow-up once a baseline of tests exists.
- Testing notifications, contact-us/review forms, S3 upload edge
  cases, or the registration verification email flow (per proposal's
  non-goals).

## Decisions

### D1: Use Django's built-in `TestCase`, no new test dependency
The project already runs `manage.py test`. Adding `pytest-django` would
mean two parallel test-running conventions with no clear benefit at
this scale. Shared setup (creating a test `Account`, `Job`, etc.) goes
in a small `TestCase` subclass per app instead of a fixtures library.

### D2: Split `tests.py` into a `tests/` package per app once it grows
`accounts/tests.py` and `main/tests.py` will each hold several test
classes across unrelated flows (auth vs. jobs vs. applications vs.
chat). Converting each to a `tests/` package (`tests/__init__.py`,
`tests/test_auth.py`, `tests/test_jobs.py`, etc.) keeps files
navigable. Decided as part of implementation, not proposal, since it's
a file-organization detail with no behavior impact.

### D3: Extend the existing ruff workflow with a separate test job, run via `uv`
Add a `test` job to `.github/workflows/ruff-check.yml` (or a sibling
workflow file — decided during apply based on which keeps the YAML
readable) that runs `uv sync` then `uv run python manage.py test`.
Alternative considered: a wholly separate CI provider/config. Rejected
— no reason to diverge from the `uv`-based workflow already adopted
project-wide.

## Risks / Trade-offs

- **A test may reveal an existing bug** (e.g., a missing ownership
  check on update/delete). → If found, report it and ask before fixing
  — this change's scope is adding tests, not silently patching
  production behavior discovered along the way.
- **CI test job needs `SECRET_KEY`/env vars to run** `manage.py test`
  reads settings via `decouple.config(...)` with no defaults for
  `SECRET_KEY`. → The CI job sets minimal required env vars (or a
  `.env` fixture for CI) so `manage.py test` can boot; `IS_PSQL` stays
  unset so it uses sqlite, no Postgres service needed in CI.

## Migration Plan

1. Add accounts auth tests (registration, login, logout).
2. Add job CRUD + permission tests.
3. Add application submission + permission tests.
4. Add chat API tests.
5. Wire a CI test job using `uv`.
6. Verify: `uv run python manage.py test` passes locally and in CI.

No rollback complexity — additive only (test files + a CI job).

## Open Questions

None — deferred concerns are captured as explicit non-goals above.
