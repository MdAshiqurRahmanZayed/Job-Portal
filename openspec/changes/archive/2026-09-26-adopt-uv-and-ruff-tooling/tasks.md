# Tasks

## 1. Add pyproject.toml (deps + ruff config)

- [x] 1.1 Create `pyproject.toml` `[project]` with direct runtime deps (`Django`, `djangorestframework`, `django-ckeditor`, `django-htmx`, `django-mptt`, `django-storages`, `django-taggit`, `django-user-visit`, `python-decouple`, `pillow`, `psycopg2-binary`, `boto3`, `gunicorn`) pinned to their current `requirements.txt` versions; verify with `uv tree` that no direct dep is missing a version
- [x] 1.2 Add a `dev` dependency group with `pre-commit` and `ruff` pinned to current versions; verify `uv tree --group dev` lists both
- [x] 1.3 Add `[tool.ruff]` (`target-version = "py310"`, `line-length = 88`, excludes for `*/migrations/*`, `staticfiles/`, `media/`, `env/`, `venv/`), `[tool.ruff.lint]` (`select = ["E", "F", "I"]`), `[tool.ruff.lint.isort]`, `[tool.ruff.format]`; verify `ruff check --show-settings . | head -30` reflects the config with no CLI flags needed

## 2. Lock and remove pip manifest

- [x] 2.1 Run `uv lock` to generate `uv.lock`; verify the file is created and `uv lock --check` reports no drift
- [x] 2.2 Run `uv sync` locally once to confirm the lock resolves cleanly; verify `uv run python manage.py check` passes
- [x] 2.3 Remove `requirements.txt` from the repo; verify `git status` shows it deleted and nothing in the repo (Dockerfile, docs, CI) still references it (`grep -rn requirements.txt . --include="*" | grep -v openspec/`)

## 3. Update Docker to install via uv

- [x] 3.1 Update `Dockerfile` to install `uv` (e.g. `COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/`) and copy `pyproject.toml` + `uv.lock` before the full `COPY . /app/`, replacing the `pip install -r requirements.txt` step with a `uv`-driven install into the system Python (not a project `.venv`, per design.md D2 — the bind mount in `docker-compose.yml` would otherwise shadow it); verify `docker build .` completes and `docker run --rm <image> uv pip list --system` (or equivalent) shows the locked versions
- [x] 3.2 Run `docker-compose -f docker-compose.yml up --build` and verify the container starts, `python manage.py migrate` runs in the entrypoint without error, and the app responds on `http://127.0.0.1:9000/`
- [x] 3.3 With the container still running, confirm dependencies remain importable inside it (e.g. `docker-compose exec web python -c "import django, rest_framework, storages"`) to verify the bind mount did not hide the installed packages

## 4. Simplify pre-commit hook

- [x] 4.1 Update `.pre-commit-config.yaml`'s `ruff` and `ruff-format` hook entries to drop the hand-written `entry:` overrides and inline `--extend-select I` flag now that rule selection lives in `pyproject.toml`; verify `pre-commit run --all-files` still runs both hooks successfully

## 5. Full-project re-lint and re-format

- [x] 5.1 Run `ruff check --fix .` against the new config across the whole project; verify exit code 0 and record whether any file changed (expected: none, since current defaults already pass clean)
- [x] 5.2 Run `ruff format .` against the new config across the whole project; verify exit code 0 and record whether any file changed (expected: none)
- [x] 5.3 If either command modified files, review the diff for unintended changes (e.g. import ordering in `migrations/` accidentally not excluded) before committing; verify `git diff --stat` only touches non-migration `.py` files

## 6. Documentation

- [x] 6.1 Update `README.md`'s local Setup section to replace `python -m venv` + `pip install -r requirements.txt` with the `uv` equivalent (`uv sync`, `uv run python manage.py ...`); verify by following the documented steps on a clean checkout
- [x] 6.2 Add/update a PythonAnywhere deployment note in `README.md` documenting the one-time manual switch on that host — install `uv`, run `uv sync` — replacing its current `pip install -r requirements.txt` step; verify the note names the exact commands to run in the PythonAnywhere console
