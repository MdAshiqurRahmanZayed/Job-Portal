# Tasks

## 1. Convert to a settings package

- [x] 1.1 Create `jobPortal/settings/` directory; move all content from `jobPortal/settings.py` into `jobPortal/settings/base.py` unchanged; verify the file diff is a pure move (no content changes) — **not actually a pure move**: `BASE_DIR = Path(__file__).resolve().parent.parent` resolved one directory level too shallow once `settings.py` became `settings/base.py` (an extra nesting level), causing `manage.py check` to report a stale `STATICFILES_DIRS` path warning; fixed by adding a third `.parent`. Caught immediately by running `manage.py check`, not assumed away.
- [x] 1.2 Create `jobPortal/settings/__init__.py` with `from .base import *`; delete the old `jobPortal/settings.py`; verify `uv run python manage.py check` passes — passes cleanly after the `BASE_DIR` fix above

## 2. Verify both toggle states

- [x] 2.1 Run `uv run python manage.py test` with `IS_PSQL` unset (sqlite path) — verify all 45 tests pass unmodified
- [x] 2.2 Run `uv run python manage.py check` with `IS_PSQL=true` (requires a reachable Postgres, e.g. via `docker compose up`) — verify no error resolving `DATABASES` — `manage.py check` validates settings/config without opening a DB connection, so this passed without a live Postgres
- [x] 2.3 Run `docker compose up --build` once — verify the app still boots and serves on `:9000` — 200, home page rendered correctly

## 3. Full verification

- [x] 3.1 Run `ruff check .` and `ruff format .` — verify clean (new package's `__init__.py`/`base.py` included)
