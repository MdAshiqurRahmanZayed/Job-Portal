# Proposal

## Why

Business logic (permission checks, model mutations, notification
creation) currently lives directly inside `main/views.py` view
functions, mixed with request/response handling. This session already
found 3 real bugs hiding in that mixing (a missing ownership check in
`updateJob`, a crashing `create_notification()` call in
`createApplication`, a crashing serializer call in
`ChatMessageAPIView`) — logic buried in views is harder to test and
review than logic isolated in a dedicated layer. Separately, the
project has no error tracking (nothing captures exceptions in
production beyond `print()`/console logs) and ships an installed-but-
never-invoked `gunicorn` dependency (the container always runs
`python manage.py runserver`, never gunicorn).

## What Changes

- Add `main/services.py` and extract the job and application business
  logic (already fully covered by the test suite added in
  `add-core-test-coverage`, so behavior-preservation is verifiable) out
  of `main/views.py`'s create/update/delete-job and
  create/view/delete-application view functions. Views keep
  request/response handling and call into services for the actual
  work. **No behavior change** — existing tests must still pass
  unmodified.
- Add Sentry error tracking (`sentry-sdk` + Django integration),
  configured via a `SENTRY_DSN` env var (optional — no-op locally when
  unset).
- Add basic Django `LOGGING` configuration (currently absent) so
  unhandled exceptions are visible somewhere before they'd hit Sentry.
- Remove the `gunicorn` dependency — confirmed unused: `Dockerfile`,
  `entrypoint.sh`, and `docker-compose.yml` all invoke
  `python manage.py runserver`, never `gunicorn`, in dev or in the
  current Docker setup.

### Explicit non-goals (deferred, not silently dropped)

- **`accounts/views.py` service extraction** — same pattern, separate
  follow-up change once the `main` extraction proves the pattern.
- **`apps/` directory regrouping** (moving `accounts`/`main` under an
  `apps/` folder) — high-risk import-path churn across the whole
  codebase for a cosmetic win; not worth it at this project's size.
- **API versioning (`api/v1/`, `api/v2/`)** — the project has exactly
  2 DRF endpoints; versioning infrastructure has no payoff yet.
- **Settings-file split** (`common.py`/`development.py`/`production.py`)
  — the project already externalizes config via `python-decouple` env
  vars, which is the substance of that convention; splitting the file
  itself is a much smaller win than the other items here.

## Capabilities

### New Capabilities
- `observability/error-tracking`: unhandled exceptions in `main` and
  `accounts` are captured and reported (Sentry), with basic logging as
  a fallback when Sentry isn't configured (e.g. local dev).

### Modified Capabilities
None — the services extraction and `gunicorn` removal are pure
internal restructuring / dependency cleanup with no spec-level
behavior change, so they carry no delta spec.

## Impact

- New file: `main/services.py`
- Modified: `main/views.py` (thinner, delegates to services),
  `jobPortal/settings.py` (Sentry init + `LOGGING`), `pyproject.toml`
  (+`sentry-sdk`, -`gunicorn`), `uv.lock`, `.env.example`
  (+`SENTRY_DSN`)
- No template, URL, or migration changes.
- Existing test suite (45 tests) must still pass unmodified after the
  services extraction — that's the behavior-preservation check.
