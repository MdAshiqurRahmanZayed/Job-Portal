# Tasks

## 1. Extract job services

- [ ] 1.1 Create `main/services.py` with `create_job(employer_profile, form) -> Job`, `update_job(job, form) -> Job`, `delete_job(job) -> None`, each taking already-validated form/instances (no `request` param, per design D1); verify with a quick `uv run python -c "import main.services"` that the module imports cleanly
- [ ] 1.2 Update `createJob`/`updateJob`/`deleteJob` in `main/views.py` to call these services, keeping the existing permission checks, `try/except`, and redirect/render behavior in the view; verify `uv run python manage.py test main.tests.test_jobs` passes unmodified

## 2. Extract application + message services

- [ ] 2.1 Move `create_notification` from `main/utilities.py` into `main/services.py` (per design D2); add `submit_application(applicant_profile, job, form) -> Application` (creates the `Application` and its notification) and `post_conversation_message(actor_profile, application, form) -> ConversationMessages` (creates the message and routes the notification to the other party); verify the module still imports cleanly
- [ ] 2.2 Update `createApplication` to call `submit_application`; update `viewApplication`'s POST branch to call `post_conversation_message`; update `deleteApplication` to call a `delete_application(application) -> None` service; verify `uv run python manage.py test main.tests.test_applications main.tests.test_chat_api` passes unmodified
- [ ] 2.3 Delete `main/utilities.py` once nothing imports it; verify `grep -rn "main.utilities\|from .utilities" --include="*.py" .` returns nothing

## 3. Log before swallowing exceptions

- [ ] 3.1 In each view that wraps a service call in `except Exception:` (per design D3), add `logger.exception(...)` before the existing `messages.warning(...)`/redirect, with a module-level `logger = logging.getLogger(__name__)` in `main/views.py`; verify by temporarily forcing one service to raise in a local test and confirming the exception is logged (then remove the temporary trigger)

## 4. Logging + Sentry

- [ ] 4.1 Add a `LOGGING` dict to `jobPortal/settings.py` (root logger at `WARNING`, console handler); verify `uv run python manage.py check` still passes and a deliberately raised exception in a shell (`uv run python manage.py shell -c "import logging; logging.getLogger('x').exception('test')"`) prints to console
- [ ] 4.2 Add `sentry-sdk` to `pyproject.toml` dependencies; run `uv lock`; verify `uv sync` resolves cleanly
- [ ] 4.3 Add Sentry init in `jobPortal/settings.py`, gated on `SENTRY_DSN` (empty/unset → no-op, per design D4); add `SENTRY_DSN=` to `.env.example` with a comment; verify `uv run python manage.py check` passes with `SENTRY_DSN` unset (no crash) and with a dummy DSN set (still starts)

## 5. Remove unused gunicorn

- [ ] 5.1 Remove `gunicorn` from `pyproject.toml`; run `uv lock`; verify `grep -rn gunicorn --include="*" . | grep -v .venv | grep -v uv.lock` shows nothing outside `openspec/changes/archive/` (historical records, left alone)

## 6. Full verification

- [ ] 6.1 Run `uv run python manage.py test` — verify all 45 tests still pass unmodified
- [ ] 6.2 Run `ruff check .` and `ruff format .` — verify clean
- [ ] 6.3 Run `docker compose up --build` once — verify the app still boots and serves on `:9000` (confirms the gunicorn removal and settings changes don't break the container)
