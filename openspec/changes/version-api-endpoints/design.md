# Design

## Context

See proposal.md - Why. Current endpoints (`main/urls.py:30-35,63-68`):
`api/conversion/` (router-registered `apiConversion` ModelViewSet) and
`api/chat-messages/<int:application_id>/` / `api/chat/`
(`ChatMessageAPIView`). Both call sites are in
`templates/main/view-application-job.html` (lines ~128, ~235), one of
which hardcodes `http://127.0.0.1:8000`.

## Goals / Non-Goals

**Goals:**
- `api/v1/` prefix on both endpoints.
- Fix the hardcoded-origin bug while touching these call sites anyway.

**Non-Goals:**
- DRF's `URLPathVersioning`/content-negotiation-based versioning
  machinery — this project has 2 endpoints; a URL prefix is
  sufficient and requires no new DRF configuration (`DEFAULT_VERSION`,
  `ALLOWED_VERSIONS`, etc.) to get right.
- Renaming `main/serializers.py`'s class or changing any
  request/response shape — purely the URL prefix and file location.

## Decisions

### D1: Plain URL-prefix versioning, not DRF's `URLPathVersioning` framework
`path("api/v1/", include([...]))` wrapping the existing router/view
registrations is sufficient. DRF's built-in versioning framework
(request.version, `DEFAULT_VERSION` setting, version-aware
serializers) solves a harder problem (multiple *simultaneously live*
versions with shared view code) that doesn't apply here — there's
only ever one live version. Adding that machinery now would be
speculative complexity for a project with 2 endpoints.

### D2: Also fix the hardcoded origin, not just note it
Since both templates being edited for the new prefix, changing
`http://127.0.0.1:8000/api/chat-messages/...` to
`/api/v1/chat-messages/...` is a strict improvement (relative URLs
work regardless of port/host) and touches the exact same line already
being edited for the prefix change — doing it separately later would
mean re-touching the same file for no reason.

## Risks / Trade-offs

- **Old URL 404s immediately** (no redirect/deprecation window) since
  there are no known external consumers (server-rendered app, only
  its own templates call these paths, and those are updated in the
  same change). → If that assumption is wrong, this is the one thing
  to double check before merging: search access logs / ask if
  anything else calls `api/conversion/` or `api/chat-messages/`.

## Migration Plan

1. Create `main/api/v1/` package; move `main/serializers.py` →
   `main/api/v1/serializers.py`, move `ChatMessageAPIView`/
   `apiConversion` → `main/api/v1/views.py`.
2. Update `main/urls.py`: import from the new location, add the
   `api/v1/` prefix.
3. Update `templates/main/view-application-job.html`'s 2 fetch calls
   to relative `/api/v1/...` paths.
4. Update `main/tests/test_chat_api.py`'s hardcoded `/api/conversion/`
   path to `/api/v1/conversion/` (its `reverse("chat-api", ...)` calls
   need no change — URL *names* are unchanged).
5. Run the full test suite; manually verify the chat feature in a
   browser against `docker compose up` (automated tests don't exercise
   the template's JS `fetch()` calls).

Rollback: revert the commit; no data/schema change.

## Open Questions

None.
