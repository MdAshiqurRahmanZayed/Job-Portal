# Proposal

## Why

`accounts/tests.py` and `main/tests.py` are 1-line Django boilerplate
stubs — there is no automated test coverage anywhere in the project.
Account registration/login, job posting/application, and the chat API
all currently rely on manual QA. A regression in any of these can ship
unnoticed. This change adds test coverage for the highest-risk, most
frequently touched flows first, rather than attempting full coverage
in one change.

## What Changes

- Add Django `TestCase`-based tests (no new test framework/dependency —
  the project already uses Django's built-in test runner via
  `manage.py test`; `DATABASES` already falls back to sqlite when
  `IS_PSQL` is unset, so tests run without a Postgres/Docker
  dependency) covering every view with actual branching logic in
  `accounts` and `main`:
  - **Accounts — auth**: registration (valid/invalid input, duplicate
    email), login (valid/invalid credentials), logout
  - **Accounts — profile onboarding**: create/update/view a user
    profile, create/update education, create/update/delete a mobile
    number, change password — all `@login_required`; each tested for
    both the happy path and the unauthenticated-rejection path
  - **Main — jobs**: create/update/delete a job (auth required,
    permission checks — only the job's creator can update/delete),
    job listing, job detail, category-filtered listing, search, and
    "my created jobs" views
  - **Main — applications**: submitting an application to a job,
    listing a user's own applications, viewing/deleting an
    application, viewing a job's applicants (employer-side),
    permission checks (applicant vs. job owner vs. unrelated user)
  - **Main — chat API**: `ChatMessageAPIView` GET/POST and the
    `apiConversion` viewset's list/create behavior
  - **Explicitly excluded as dead code, not just deprioritized**:
    `sendMessages` and `chat_messages` in `main/views.py` — both are
    unreachable stubs (hardcoded return values, no template, not
    linked from anywhere); testing them would test nothing real
- Add a CI job (or extend the existing ruff workflow) to run
  `uv run python manage.py test` on every PR, so this coverage is
  enforced going forward, not just written once.

## Capabilities

### New Capabilities
- `testing/core-flows`: automated test coverage for the account
  registration/auth flow, job posting/application flow, and the chat
  API — the highest-traffic, highest-risk paths in the app.

### Modified Capabilities
None.

## Impact

- Modified: `accounts/tests.py`, `main/tests.py` (or split into a
  `tests/` package per app if the file grows large — decided during
  apply)
- Modified: a GitHub Actions workflow to run tests on PRs
- No production code changes anticipated; if a test reveals an actual
  bug (e.g. a missing permission check), that will be surfaced and
  asked about before being silently fixed as a drive-by change.
- Out of scope (explicit non-goals, not a full audit): notifications
  (`notifications`, `notifications_count*`), static/informational
  views (`home`, `contactUs`, `Review_website`, `About_page`), the
  dead `sendMessages`/`chat_messages` stubs, S3 file upload edge
  cases, the email-verification token flow (`activate`), and 100%
  branch coverage. These can be follow-up changes.
