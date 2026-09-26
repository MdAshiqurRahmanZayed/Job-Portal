# Tasks

## 1. Move API code into a versioned package

- [x] 1.1 Create `main/api/v1/__init__.py`, `main/api/v1/serializers.py` (moved from `main/serializers.py`), `main/api/v1/views.py` (moved `ChatMessageAPIView` and `apiConversion` from `main/views.py`); verify `uv run python -c "import main.api.v1.views"` imports cleanly
- [x] 1.2 Update `main/urls.py` to import from `main.api.v1.views` and wrap the router/chat paths under an `api/v1/` prefix; verify `uv run python manage.py test main.tests.test_chat_api` fails only on the one hardcoded-path assertion (expected until task 2.1)

## 2. Update tests and templates for the new prefix

- [x] 2.1 Update `main/tests/test_chat_api.py`'s hardcoded `/api/conversion/` calls to `/api/v1/conversion/`; verify `uv run python manage.py test main.tests.test_chat_api` passes fully
- [x] 2.2 Update `templates/main/view-application-job.html`'s 2 fetch calls: replace `http://127.0.0.1:8000/api/chat-messages/...` with `/api/v1/chat-messages/...`, and `http://127.0.0.1:8000/api/conversion/` (if present) with `/api/v1/conversion/`; verify by grepping the file for `127.0.0.1` and confirming no matches remain — confirmed; one commented-out (dead) line still mentions the old URL, left as-is since it's unreachable

## 3. Full verification

- [x] 3.1 Run `uv run python manage.py test` — verify all tests pass
- [x] 3.2 Run `docker compose up --build`, open a job application's chat view in a browser, send a message — verify the chat feature still works end-to-end against the new `/api/v1/` paths (automated tests don't exercise the template's JS `fetch()` calls) — container boots and serves 200; manual browser click-through of the chat feature itself not performed (no interactive browser session in this environment) — recommend a quick manual check before merging
- [x] 3.3 Run `ruff check .` and `ruff format .` — verify clean
