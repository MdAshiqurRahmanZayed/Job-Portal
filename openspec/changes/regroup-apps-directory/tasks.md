# Tasks

## 1. Move directories

- [x] 1.1 `git mv accounts apps/accounts`, `git mv main apps/main`; verify `git status` shows renames, not delete+add, and no content diff on any moved file (`git diff --stat` between old and new paths shows only path changes) — `git mv` failed on `main/` because `main/serializers.py` was already deleted in the (uncommitted) working tree from the earlier Phase 4 change, and there were new untracked files (`main/services.py`, `main/api/`, `apps/accounts/services.py`) `git mv` wouldn't carry along; used plain `mv main apps/main` instead, will reconcile with `git add -A` before committing

## 2. Update settings, URLs, and imports

- [x] 2.1 Update `INSTALLED_APPS` (`"main"`→`"apps.main"`, `"accounts"`→`"apps.accounts"`); run `uv run python manage.py makemigrations --check --dry-run`; verify it reports no changes (per design.md D1/Risks — if it does report a change, add explicit `AppConfig.label` overrides and re-run until clean, before proceeding to any other task) — required also updating `AppConfig.name` in each app's `apps.py` (was hardcoded to the old bare module name); confirmed only a pre-existing, unrelated `user_visit` (3rd-party) migration is pending — zero drift for `accounts`/`main`
- [x] 2.2 Update `jobPortal/urls.py`'s `include("main.urls")`/`include("accounts.urls")` to `include("apps.main.urls")`/`include("apps.accounts.urls")`; verify `uv run python manage.py check` passes
- [x] 2.3 Re-grep for cross-app imports (`grep -rln "from accounts\.\|from main\.\|^import accounts\b\|^import main\b" --include="*.py" apps/ jobPortal/`) and update each to `apps.accounts`/`apps.main`; verify the grep returns nothing afterward — 12 files (11 planned + 1 new from Phase 4's `api/v1/`). **Also found (not caught by this grep pattern):** dotted-path *string* references in `jobPortal/settings/base.py` (`TEMPLATES` context_processors and the `custom_filters` library path) still pointed at `main.*` — these aren't `from`/`import` statements so the grep missed them; found via the actual `InvalidTemplateLibrary` error, fixed alongside

## 3. Full verification

- [x] 3.1 Run `uv run python manage.py test` — verify all tests pass unmodified
- [x] 3.2 Run `ruff check .` and `ruff format .` — verify clean
- [x] 3.3 Run `docker compose up --build` — verify the app boots and serves on `:9000` — 200, and `docker compose exec web python manage.py test` ran 45/45 passing inside the container too
