# dev-tooling/python-environment Specification

## Purpose

Defines a reproducible Python dependency environment and an enforced
lint/format standard shared by local development, Docker builds, and
the project's pip-based deployment fallback.

## Requirements

### Requirement: Reproducible dependency resolution
The project SHALL provide a locked dependency manifest so that
installing dependencies from a clean checkout produces the exact same
resolved versions every time, regardless of when or where the install
runs.

#### Scenario: Fresh clone install
- **WHEN** a developer runs the project's documented install command on
  a clean checkout
- **THEN** the exact dependency versions recorded in the lock file are
  installed, with no other version allowed to resolve

### Requirement: Docker image installs from the lock file
The Docker image build SHALL install dependencies from the committed
lock file rather than re-resolving them, so the image is reproducible
across builds and machines.

#### Scenario: Image build installs locked versions
- **WHEN** the Docker image is built
- **THEN** the installed dependency versions match the committed lock
  file exactly

#### Scenario: Bind-mounted dev container still runs
- **WHEN** the container starts under `docker-compose.yml`, which
  bind-mounts the full repository over the application directory
- **THEN** the installed dependencies remain available to the running
  application (they are not hidden by the bind mount)

### Requirement: uv is the only supported dependency installer
The project SHALL NOT ship or require a `pip`-compatible dependency
manifest (e.g. `requirements.txt`). Every environment that runs this
project — local development, Docker, and any deployment host —
installs dependencies with `uv` from the committed lock file.

#### Scenario: No pip manifest present
- **WHEN** the repository is inspected for a dependency manifest
- **THEN** no `requirements.txt` (or equivalent plain-pip manifest)
  exists — only `pyproject.toml` and `uv.lock`

### Requirement: Whole-codebase lint and format compliance
The full Python codebase (excluding `migrations/`, `staticfiles/`, and
`media/`) SHALL pass lint and format checks against the project's
pinned configuration.

#### Scenario: Full-project check passes
- **WHEN** the project's lint check and format check are run over the
  entire codebase
- **THEN** both complete with no reported violations and no files left
  unformatted
