# Tasks

## 1. Extract job services

- [x] 1.1 Create `main/services.py` with `create_job(employer_profile, form) -> Job`, `update_job(job, form) -> Job`, `delete_job(job) -> None`, each taking already-validated form/instances (no `request` param, per design D1); verify with a quick `uv run python -c "import main.services"` that the module imports cleanly
- [x] 1.2 Update `createJob`/`updateJob`/`deleteJob` in `main/views.py` to call these services, keeping the existing permission checks, `try/except`, and redirect/render behavior in the view; verify `uv run python manage.py test main.tests.test_jobs` passes unmodified

## 2. Extract application + message services

- [x] 2.1 Move `create_notification` from `main/utilities.py` into `main/services.py` (per design D2); add `submit_application(applicant_profile, job, form) -> Application` (creates the `Application` and its notification) and `post_conversation_message(actor_profile, application, form) -> ConversationMessages` (creates the message and routes the notification to the other party); verify the module still imports cleanly
- [x] 2.2 Update `createApplication` to call `submit_application`; update `viewApplication`'s POST branch to call `post_conversation_message`; update `deleteApplication` to call a `delete_application(application) -> None` service; verify `uv run python manage.py test main.tests.test_applications main.tests.test_chat_api` passes unmodified — note: `Notification.objects.filter(extra_id=...).delete()` deliberately left unconditional in the view (pre-existing behavior: it wipes notifications on a bare GET, before any ownership/POST check), not moved into the service, to avoid silently changing that behavior during a refactor scoped as behavior-preserving
- [x] 2.3 Delete `main/utilities.py` once nothing imports it; verify `grep -rn "main.utilities\|from .utilities" --include="*.py" .` returns nothing

## 3. Log before swallowing exceptions

- [x] 3.1 In each view that wraps a service call in `except Exception:` (per design D3), add `logger.exception(...)` before the existing `messages.warning(...)`/redirect, with a module-level `logger = logging.getLogger(__name__)` in `main/views.py`; verify by temporarily forcing one service to raise in a local test and confirming the exception is logged (then remove the temporary trigger) — verified: forced `create_job` to raise, confirmed "Failed to create job" + traceback appeared in test output, then removed the forced failure

## 4. Logging + Sentry

- [x] 4.1 Add a `LOGGING` dict to `jobPortal/settings.py` (root logger at `WARNING`, console handler); verify `uv run python manage.py check` still passes and a deliberately raised exception in a shell (`uv run python manage.py shell -c "import logging; logging.getLogger('x').exception('test')"`) prints to console
- [x] 4.2 Add `sentry-sdk` to `pyproject.toml` dependencies; run `uv lock`; verify `uv sync` resolves cleanly
- [x] 4.3 Add Sentry init in `jobPortal/settings.py`, gated on `SENTRY_DSN` (empty/unset → no-op, per design D4); add `SENTRY_DSN=` to `.env.example` with a comment; verify `uv run python manage.py check` passes with `SENTRY_DSN` unset (no crash) and with a dummy DSN set (still starts) — note: appended to `.env.example` blind (can't read/grep `.env*` files per this project's permission rules); flagged a possible duplicate line for the user to check manually

## 5. Remove unused gunicorn

- [x] 5.1 Remove `gunicorn` from `pyproject.toml`; run `uv lock`; verify `grep -rn gunicorn --include="*" . | grep -v .venv | grep -v uv.lock` shows nothing outside `openspec/changes/archive/` (historical records, left alone) — confirmed only this change's own planning docs (proposal/design/tasks) reference it now, no code

## 6. Full verification

- [x] 6.1 Run `uv run python manage.py test` — verify all 45 tests still pass unmodified
- [x] 6.2 Run `ruff check .` and `ruff format .` — verify clean
- [x] 6.3 Run `docker compose up --build` once — verify the app still boots and serves on `:9000` (confirms the gunicorn removal and settings changes don't break the container) — verified 200 on `:9000`
