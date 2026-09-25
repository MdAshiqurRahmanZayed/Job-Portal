# Proposal

## Why

The repo currently manages Python dependencies with a hand-maintained,
flat `requirements.txt` (direct and transitive packages mixed together,
`pip install -r requirements.txt`) and lints/formats with `ruff` on
unpinned defaults (no `pyproject.toml`, rules only implied by a
pre-commit hook flag). This makes dependency resolution
non-reproducible (no lock file, no hash pinning), makes the effective
lint/format rule set invisible outside the pre-commit hook, and means
the Docker image reinstalls the entire flat list with plain `pip` on
every build. Adopting `uv` for dependency management (with a lock
file) and pinning an explicit `ruff` config in `pyproject.toml` fixes
both. `pip`/`requirements.txt` is dropped entirely — `uv` becomes the
only supported way to install dependencies, everywhere this project
runs, including the PythonAnywhere host.

## What Changes

- Add `pyproject.toml` as the single source of truth for:
  - `[project]` direct runtime dependencies (identified from
    `INSTALLED_APPS`/imports, not copied wholesale from the flat
    `requirements.txt`)
  - a `dev` dependency group (`pre-commit`, `ruff`)
  - `[tool.ruff]` / `[tool.ruff.lint]` / `[tool.ruff.lint.isort]` /
    `[tool.ruff.format]` pinning target Python version, line length,
    rule set (`E`, `F`, `I`), and excludes (`migrations/`,
    `staticfiles/`, `media/`)
- Add `uv.lock` (generated, committed) for reproducible installs.
- Remove `requirements.txt` — no pip-based install path is kept, on any
  host. **BREAKING** for the PythonAnywhere deployment: its console
  session must install `uv` and run `uv sync` (documented in
  `README.md`) instead of `pip install -r requirements.txt` on the next
  deploy.
- Update `Dockerfile` to install dependencies with `uv` instead of
  `pip install -r requirements.txt` (installing into the system Python,
  not a project `.venv`, since `docker-compose.yml` bind-mounts the
  full repo over `/app` and would otherwise shadow an in-project venv
  built at image-build time). **BREAKING** for anyone relying on the
  current `pip`-based Docker build steps directly.
- Simplify `.pre-commit-config.yaml`'s `ruff`/`ruff-format` hook entries
  now that rule selection lives in `pyproject.toml`.
- Run `ruff check --fix .` and `ruff format .` across the full project
  against the new pinned config and commit any resulting diffs.
- Update `README.md`'s setup section (local **and** PythonAnywhere) to
  use `uv` instead of `python -m venv` + `pip install -r
  requirements.txt`.

## Capabilities

### New Capabilities
- `dev-tooling/python-environment`: reproducible Python dependency
  installs via `uv` everywhere this project runs (local, Docker,
  PythonAnywhere), and a pinned, enforced lint/format standard across
  the whole codebase.

### Modified Capabilities
None — no existing `openspec/specs/` capabilities exist yet in this
project.

## Impact

- New files: `pyproject.toml`, `uv.lock`
- Removed: `requirements.txt`
- Modified: `Dockerfile`, `.pre-commit-config.yaml`, `README.md`
- Whatever `.py` files (outside `migrations/`) need reformatting once
  the explicit ruff config is in place — expected to be zero or
  near-zero since current defaults already pass clean, confirmed
  during apply.
- `docker-compose.yml`: no command/port changes expected, but the image
  rebuild behavior changes (verified during apply).
- No Django application runtime behavior changes.
