# Design

## Context

See proposal.md - Why. Concretely, `main/views.py` currently has 7
functions mixing permission checks, ORM writes, and notification calls
directly with request/response handling: `createJob`, `updateJob`,
`deleteJob`, `createApplication`, `viewApplication` (its POST branch,
which posts a chat message), `deleteApplication`. All 7 are covered by
`add-core-test-coverage`'s test suite (`main/tests/test_jobs.py`,
`test_applications.py`) — that suite is the safety net for this
refactor: it must pass unmodified before and after.

A recurring pattern in the current code is a bare `except Exception:`
around the service-like logic, which is exactly how bug #2
(`createApplication`'s crashing `create_notification()` call) went
unnoticed — the exception was swallowed with a generic user-facing
message and never logged anywhere.

No existing `LOGGING` config or error tracking exists in
`jobPortal/settings.py`.

## Goals / Non-Goals

**Goals:**
- Move ORM writes + notification-triggering logic for jobs and
  applications out of views into `main/services.py`, functions that
  take plain arguments (not `request`) and return model instances or
  raise, so they're independently testable.
- Wherever a view still needs a broad `except Exception:` around a
  service call (to keep today's "show a friendly message, don't 500"
  behavior), log the exception first so it doesn't disappear silently
  the way bug #2 did.
- Add Sentry + `LOGGING` so exceptions are visible/reported without
  requiring this refactor to eliminate every broad except.
- Remove the confirmed-unused `gunicorn` dependency.

**Non-Goals:**
- Rewriting `viewApplication`'s GET branch, `allApplication`, or any
  read-only view — only the state-mutating logic moves.
- Changing any URL, template, or JSON contract.
- `accounts/views.py` extraction (separate follow-up, see proposal).
- Adding gunicorn back / changing how the app is served — removing it
  only removes an unused dependency, it does not touch
  `entrypoint.sh`/`Dockerfile`'s `runserver` command.

## Decisions

### D1: Services take plain arguments, not `request`
`create_notification(request, ...)` currently derives
`request.user.userprofile` from the request object. The new service
functions take the already-resolved `UserProfile` explicitly instead,
e.g. `submit_application(applicant_profile, job, form) -> Application`
internally calls `create_notification`-equivalent logic itself. This
makes services callable from a test or a shell without constructing a
fake request, and matches how `main/tests/*` already builds fixtures
directly against models/profiles.

Alternative considered: pass `request` through to services for
minimal diff. Rejected — it re-couples services to Django's request
cycle, defeating the point of extracting them.

### D2: `main/utilities.py`'s `create_notification` moves into `services.py` too
It's already a small piece of the same business logic
(`Notification.objects.create(...)`), currently imported separately.
Consolidating avoids having "some business logic in services.py,
some in utilities.py" as a second place to look.

### D3: Exception handling in views: log first, then show the friendly message
Where a view still wraps a service call in
`except Exception:` (matching today's behavior of "show a friendly
error, don't crash"), add `logger.exception(...)` before the
`messages.warning(...)` / redirect, so Sentry (via its logging
integration) and local console logs both capture it. This directly
targets the failure mode that hid bug #2.

### D4: Sentry via `sentry-sdk`'s Django integration, DSN-gated
`sentry_sdk.init(dsn=config("SENTRY_DSN", default=""), integrations=[DjangoIntegration()], ...)`
guarded so an empty/unset DSN means Sentry does nothing (no error, no
network calls) — matches local dev having no DSN configured.

Alternative considered: only enable Sentry when `not DEBUG`. Rejected
as an additional implicit condition — an explicit env var is simpler
to reason about and matches how `USE_S3`/`IS_PSQL` are already gated
in this codebase.

### D5: Remove `gunicorn` from `pyproject.toml`, regenerate `uv.lock`
No wiring anywhere invokes it (confirmed via repo-wide grep before
writing this proposal). If a future change wants to serve via
gunicorn instead of `runserver`, that's a separate decision that would
re-add it deliberately with an accompanying `Dockerfile`/entrypoint
change.

## Risks / Trade-offs

- **Refactor regressions**: moving logic could subtly change behavior.
  → Mitigation: the existing 45-test suite must pass unmodified
  after the extraction; no test file changes are part of this change.
- **Sentry DSN handling**: a malformed but non-empty `SENTRY_DSN` could
  make `sentry_sdk.init` raise at startup. → Mitigation: rely on
  `sentry-sdk`'s own validation (it already no-ops on a clearly invalid
  DSN rather than crashing); document the env var in `.env.example`.
- **`LOGGING` config verbosity**: too much console noise. → Mitigation:
  keep it minimal (root logger at `WARNING`, Django's own logger
  unchanged) rather than instrumenting everything at once.

## Migration Plan

1. Add `main/services.py` with the extracted functions + moved
   `create_notification`.
2. Update `createJob`/`updateJob`/`deleteJob` to call the job services;
   run job tests.
3. Update `createApplication`/`viewApplication`/`deleteApplication` to
   call the application/message services, with `logger.exception(...)`
   added to their broad excepts; run application tests.
4. Delete `main/utilities.py` (superseded by `services.py`) once
   nothing imports it.
5. Add `LOGGING` to `jobPortal/settings.py`.
6. Add `sentry-sdk` dependency, Sentry init gated on `SENTRY_DSN`,
   document the env var in `.env.example`.
7. Remove `gunicorn` from `pyproject.toml`; `uv lock`.
8. Run the full test suite; run `ruff check`/`ruff format`.

Rollback: revert the commit(s); no data migration, no schema change.

## Open Questions

None — deferred items are captured as explicit non-goals in the
proposal.
