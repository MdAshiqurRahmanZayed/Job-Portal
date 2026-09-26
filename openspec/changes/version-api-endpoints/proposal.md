# Proposal

## Why

The 2 DRF endpoints (`api/conversion/` → `apiConversion` ModelViewSet,
`api/chat-messages/<id>/` and `api/chat/` → `ChatMessageAPIView`) have
no version prefix. Adding one now, while there are only 2 endpoints
and 2 call sites, is far cheaper than doing it after the API grows.
While auditing the call sites, found a second real bug worth fixing in
the same change: `templates/main/view-application-job.html` hardcodes
`http://127.0.0.1:8000` as the fetch origin for the chat API — this
already silently breaks in the current Docker setup (port `9000`, not
`8000`) and would break in any other deployment; it should use a
relative path instead, which also removes the versioning migration's
main risk (forgetting a hardcoded absolute URL).

## What Changes

- Move `main/serializers.py` and the 2 DRF view classes
  (`ChatMessageAPIView`, `apiConversion`) into `main/api/v1/`
  (`serializers.py`, `views.py`), re-exported/imported from
  `main/urls.py`.
- Change URL prefixes: `api/conversion/` → `api/v1/conversion/`,
  `api/chat-messages/<id>/` → `api/v1/chat-messages/<id>/`, `api/chat/`
  → `api/v1/chat/`. **BREAKING** for the prefix change itself.
- Fix `templates/main/view-application-job.html`'s 2 hardcoded
  `http://127.0.0.1:8000/...` fetch URLs to use relative paths
  (`/api/v1/...`), fixing the pre-existing port-mismatch bug and the
  two call sites needing an update anyway for the new prefix.

## Capabilities

### New Capabilities
- `api/versioning`: the project's DRF endpoints live under a
  versioned `api/v1/` prefix, and callers must use that prefix and a
  relative (not hardcoded-origin) URL.

### Modified Capabilities
None.

## Impact

- New: `main/api/v1/serializers.py`, `main/api/v1/views.py`
- Removed: `main/serializers.py` (moved), the 2 view classes removed
  from `main/views.py` (moved)
- Modified: `main/urls.py` (new prefixes), 1 template (2 fetch calls)
- `main/tests/test_chat_api.py` (9 tests) reference `reverse("chat-api")`
  and the raw path `/api/conversion/` — the `reverse()` calls keep
  working unchanged (URL *names* don't change, only their resolved
  path); the raw-path test needs updating to `/api/v1/conversion/`.
- **Breaking for any external API consumer** — none are known to
  exist (this is a server-rendered app; the only consumers are the
  project's own templates, updated as part of this change), but flagged
  explicitly since URL-path changes are inherently breaking.
