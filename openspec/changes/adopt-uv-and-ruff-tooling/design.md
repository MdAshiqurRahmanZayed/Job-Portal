# Design

## Context

See proposal.md - Why. Current state relevant to this design:

- `requirements.txt` is a flat pip-freeze mixing direct and transitive
  packages, no lock file, no hashes.
- `Dockerfile` does `pip install --no-cache-dir -r requirements.txt`.
- `docker-compose.yml` bind-mounts the whole repo (`.:/app`) over the
  image's `/app` at runtime, for live-reload dev.
- The project is also live-deployed on PythonAnywhere (per README),
  which currently installs with plain `pip install -r requirements.txt`
  in a console session. This change drops `pip`/`requirements.txt`
  entirely, so that host's install step must switch to `uv` too on the
  next deploy.
- No `pyproject.toml` exists; `ruff` runs on defaults plus a
  `--extend-select I` flag hardcoded into the pre-commit hook entry.

## Goals / Non-Goals

**Goals:**
- Reproducible, locked dependency installs for local dev, CI/pre-commit,
  and Docker.
- Docker image builds using `uv`, without breaking the bind-mounted
  dev workflow in `docker-compose.yml`.
- Pinned, explicit `ruff` configuration; full codebase passes it.
- `uv` as the only supported installer everywhere, including
  PythonAnywhere — no `pip`/`requirements.txt` path kept.

**Non-Goals:**
- Actually running the PythonAnywhere console commands to switch that
  host over (documented in README as a required manual step; the host
  itself isn't reachable from this change).
- Switching the dev/prod process manager (still `python manage.py
  runserver` via `docker-compose.yml`; `gunicorn` stays an installed
  but unwired dependency, unchanged from today).
- Expanding the `ruff` rule set beyond current effective behavior
  (`E`, `F`, `I`) — that's a separate future change if wanted.

## Decisions

### D1: `pyproject.toml` + `uv.lock` are the only dependency manifests; `requirements.txt` is removed
Direct dependencies were identified from `INSTALLED_APPS`
(`jobPortal/settings.py`) and actual imports (`ckeditor`, `decouple`,
`rest_framework`, `storages`, `taggit`, `django_htmx`, `mptt`,
`user_visit`), plus `psycopg2-binary` (DB backend), `pillow` (image
fields), `boto3` (S3 storage backend), and `gunicorn` (already present,
kept for parity even though not currently wired into the container
command). Packages like `asgiref`, `certifi`, `six`, `urllib3`,
`ua-parser*`, `django-js-asset`, and pre-commit's own transitive deps
(`cfgv`, `identify`, `nodeenv`, `virtualenv`, `distlib`, `filelock`,
`platformdirs`) are not listed directly — `uv` resolves and locks them
automatically as transitive dependencies.
`dev` dependency group: `pre-commit`, `ruff`.

Alternative considered: keep a generated `requirements.txt` (via `uv
export`) as a `pip` fallback for PythonAnywhere. Rejected per explicit
instruction — no `pip` path anywhere, including that host; its console
session installs `uv` and runs `uv sync` instead.

### D2: Docker installs with `uv pip install --system`, not `uv sync`
`uv sync` creates a project-local `.venv` and expects the project
directory to stay stable. Because `docker-compose.yml` bind-mounts the
host repo over `/app` at container start (`volumes: - .:/app`), a
`.venv` built into `/app` during image build would be shadowed by the
bind mount and disappear at runtime — breaking the container.
`uv pip install --system` installs into the system Python instead (no
project venv, nothing under `/app` to be shadowed), which mirrors
today's `pip install` behavior and sidesteps the mount problem
entirely.

Alternative considered: put the venv outside `/app` (e.g.
`UV_PROJECT_ENVIRONMENT=/opt/venv` + adjust `PATH`). Rejected as more
moving parts for no benefit here — this project doesn't need an
isolated venv inside a single-purpose container image.

### D3: Ruff config lives in the same new `pyproject.toml`
Combines the previously-planned ruff pinning (target Python version,
line length, `select = ["E", "F", "I"]`, excludes) into this same file
rather than a separate `ruff.toml`, since `pyproject.toml` is being
introduced anyway.

## Risks / Trade-offs

- **PythonAnywhere breaks at next deploy**: removing
  `requirements.txt` breaks that host's existing `pip install -r
  requirements.txt` step immediately. → Mitigation: document the `uv`
  install/sync steps for that host in README's setup section as part
  of this change; this is a manual, one-time update the operator must
  apply on the host itself before the next deploy there.
- **Docker layer cache change**: build previously copied
  `requirements.txt` first for caching; now copies `pyproject.toml` +
  `uv.lock` first. → Verified during apply that the build still caches
  the dependency-install layer across unrelated code changes.
- **Pillow / psycopg2 native deps**: both ship manylinux wheels and the
  existing `apt-get install` list already covers `libpq-dev`/`gcc`
  needed for anything that falls back to source. → No new system
  packages expected; verified by a full `docker build`.

## Migration Plan

1. Add `pyproject.toml` (deps + dev group + ruff config).
2. Run `uv lock` to generate `uv.lock`; commit it.
3. Remove `requirements.txt` from the repo.
4. Update `Dockerfile`: install `uv`, copy `pyproject.toml` + `uv.lock`
   early, replace the `pip install` step with a `uv`-driven install
   into the system Python (no project venv, per D2).
5. Simplify `.pre-commit-config.yaml` ruff hook entries.
6. Run `ruff check --fix .` and `ruff format .` across the repo; commit
   any diff.
7. Update `README.md`: local setup uses `uv`; add a PythonAnywhere
   section documenting the `uv` install/sync steps replacing `pip
   install -r requirements.txt` there.
8. Verify `docker-compose up --build` still boots, runs migrations, and
   serves the app on port 9000.

No rollback complexity beyond reverting the commit(s) — no data
migrations, no schema changes, no external service changes.

## Open Questions

None — all decisions above are resolved; nothing here would change the
spec, approach, or task breakdown if answered later.
