# Proposal

## Why

`jobPortal/settings.py` is a single 198-line file with inline
environment branching (`if IS_PSQL: ... else: ...`, `if USE_S3: ...
else: ...`) mixing base config, database config, and storage config
in one file. It already externalizes secrets/toggles via
`python-decouple` (the substance of a settings split), but a
`base.py`/`development.py`/`production.py` layout makes it clearer
which settings are environment-specific at a glance, without needing
to trace `if IS_PSQL`/`if USE_S3` branches.

- Convert `jobPortal/settings.py` into a `jobPortal/settings/` package
  with `base.py` (all current content, unchanged) and `__init__.py`
  (`from .base import *`).
  **Note (see design.md D1):** `IS_PSQL` and `USE_S3` are independent
  toggles today, not a single dev/prod switch, so a
  `development.py`/`production.py` split as originally sketched here
  would misrepresent that independence. This proposal was revised
  after that was found during design — see design.md for the full
  reasoning. A true dev/prod file split is a separate, deliberate
  future proposal if still wanted.
- Verify `DJANGO_SETTINGS_MODULE` (`manage.py`, `wsgi.py`/`asgi.py`)
  still resolves once `settings.py` becomes `settings/__init__.py`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
None — purely reorganizing where settings live; no setting's value or
behavior changes. `skip_specs: true` is set in `.openspec.yaml`.

## Impact

- `jobPortal/settings.py` → `jobPortal/settings/{__init__,base,development,production}.py`
- No behavior change: `IS_PSQL=true` still selects Postgres/S3,
  `IS_PSQL` unset/false still selects sqlite/local storage — same as
  today.
- Verify via `manage.py check` and the full test suite that nothing
  broke, since Django's settings resolution is easy to get subtly
  wrong (e.g. forgetting an import in a submodule).
