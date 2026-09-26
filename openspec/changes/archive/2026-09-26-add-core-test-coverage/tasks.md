# Tasks

## 1. Accounts: auth flow tests

- [x] 1.1 Convert `accounts/tests.py` into an `accounts/tests/` package (`__init__.py`, `test_auth.py`) with a shared `TestCase` base creating a reusable test `Account`; verify `uv run python manage.py test accounts` collects and runs with no import errors
- [x] 1.2 Add registration tests: valid input creates an `Account`; duplicate email is rejected and no second account is created; verify both pass
- [x] 1.3 Add login/logout tests: correct credentials authenticate the session; incorrect password is rejected; logout ends the session; verify all pass

## 2. Accounts: profile onboarding

- [x] 2.1 Add `test_profile.py`: authenticated profile create/update persists a `UserProfile`; unauthenticated requests are redirected to login and change nothing; verify both pass
- [x] 2.2 Add education create/update tests: authenticated requests persist correctly; unauthenticated requests are rejected; verify both pass
- [x] 2.3 Add mobile-number create/update/delete tests: authenticated requests persist/remove the record; unauthenticated requests are rejected; verify all pass
- [x] 2.4 Add a change-password test: authenticated user can change their password and can subsequently log in with the new one; verify it passes

## 3. Main: job CRUD, filtering, and permissions

- [x] 3.1 Convert `main/tests.py` into a `main/tests/` package (`__init__.py`, `test_jobs.py`) with a shared base creating a test `Account` + `Category`; verify `uv run python manage.py test main` collects with no import errors
- [x] 3.2 Add job creation tests: authenticated create succeeds and persists a `Job`; unauthenticated create is redirected to login and creates nothing; verify both pass
- [x] 3.3 Add job update/delete permission tests: the job's creator can update/delete it; a different authenticated user cannot; verify both pass, and if either currently fails against existing view code, report the finding and pause rather than silently patching the view — **found and fixed**: `updateJob` (main/views.py) had no ownership check at all (any employer could update any job); added the missing `request.user.userprofile != job.user` check, mirroring `deleteJob`
- [x] 3.4 Add job listing/detail view tests: listing returns existing jobs; detail view returns the requested job's data; verify both pass
- [x] 3.5 Add category-filter and search tests: category filter returns only matching jobs; search returns jobs matching the term; verify both pass
- [x] 3.6 Add "my created jobs" test: an authenticated user's created-jobs view returns only their own jobs, not other users' jobs; verify it passes

## 4. Main: application submission and permissions

- [x] 4.1 Add `test_applications.py`: authenticated user submitting an application to an existing job creates an `Application` record linking user and job; verify it passes — **found and fixed**: `createApplication` called `create_notification(...)` without the required `application=` kwarg, raising a `TypeError` swallowed by a bare `except Exception`, silently reporting "not completed" even though the `Application` had saved; passed `application=form` through
- [x] 4.2 Add applicant-side listing test: an authenticated user's applications-list view returns only their own applications; verify it passes
- [x] 4.3 Add employer-side applicants test: a job's creator can view its applicants; a non-owner cannot; verify both pass, and if the non-owner case currently fails against existing view code, report the finding and pause — passed as-is (`allApplicant` already scopes via `get_object_or_404(Job, id=pk, user=request.user.userprofile)`, correctly 404s for non-owners)
- [x] 4.4 Add permission tests: a user who is neither the applicant nor the job owner cannot view or delete the `Application`; verify it passes, and if it currently fails against existing view code, report the finding and pause — passed as-is (both views scope via `get_object_or_404`)

## 5. Main: chat API tests

- [x] 5.1 Add `test_chat_api.py` covering `ChatMessageAPIView`: authenticated GET returns existing `ConversationMessages` for a conversation; authenticated POST with valid data creates a message; POST with invalid/missing data is rejected with an error response and creates nothing; verify all three pass — **found and fixed**: `ChatMessageAPIView.post` passed `application__id=application_id` directly into `ChatMessageSerializer(...)`, which isn't a valid serializer kwarg and crashed with `TypeError` on every POST; now builds `data["application"] = application_id` before validating
- [x] 5.2 Add coverage for the `apiConversion` `ModelViewSet`'s list/create behavior at `api/conversion/`; verify it passes

## 6. CI wiring

- [x] 6.1 Add a `test` job to `.github/workflows/ruff-check.yml` (or a new sibling workflow, whichever keeps the YAML clearer) that installs `uv`, runs `uv sync`, sets the minimal env vars `manage.py test` needs to boot (e.g. `SECRET_KEY`), and runs `uv run python manage.py test`; verify by pushing the branch and confirming the job runs and passes in GitHub Actions — added as a new sibling workflow `.github/workflows/test.yml`, deliberately not touching `ruff-check.yml` (its own unpinned-`pip` fix is a separately deferred item); GitHub Actions run pending push
- [x] 6.2 Run the full suite locally once more end-to-end (`uv run python manage.py test`) and record pass/fail counts in the PR description — 45/45 passed locally with only `SECRET_KEY`/`IS_PSQL=false` set (no reliance on local `.env`)
- [x] 6.3 Add a "Running Tests" section to `README.md` documenting both `uv run python manage.py test` (local) and `docker compose exec web python manage.py test` (Docker); verify both documented commands actually work as written — verified both: 45/45 pass locally and 45/45 pass inside a rebuilt Docker container
