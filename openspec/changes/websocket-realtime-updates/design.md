# Design

## Context

See proposal.md - Why. Relevant current state:

- `jobPortal/asgi.py` and `wsgi.py` both already exist as bare Django
  scaffolds; nothing currently uses the ASGI one (Docker/`runserver`
  use WSGI).
- Auth is session-based (`django.contrib.sessions` + custom
  `Account`/`AbstractBaseUser` model, `AUTH_USER_MODEL =
  "accounts.Account"`) — Channels' `AuthMiddlewareStack` reads the
  session cookie the same way Django's WSGI auth middleware does, so
  no new auth mechanism is needed for the WebSocket handshake.
- `apps/main/services.py`'s `create_notification` and
  `post_conversation_message` are the only two places that create
  `Notification`/`ConversationMessages` records today (confirmed by
  grep — `submit_application` and `viewApplication`'s POST branch are
  the only callers).
- `viewApplication` (main/views.py) already implements the exact
  permission check a `ChatConsumer` needs: employer → application
  scoped to `job__user=request.user.userprofile`; jobseeker →
  scoped to `user=request.user.userprofile`.
- Docker: `docker-compose.yml` has one `web` service, no other
  services; `Dockerfile` installs deps via `uv` into the system
  Python and runs via `entrypoint.sh` → `python manage.py runserver`
  (WSGI dev server).

## Goals / Non-Goals

**Goals:**
- Real-time push for notifications and chat messages, replacing the
  2s/1s polling loops.
- Reuse existing session auth and existing permission-checked HTTP
  write paths — WebSocket is push-only.
- Minimal new test surface: Channels' `WebsocketCommunicator`, scoped
  to the 2 consumers.

**Non-Goals:**
- Client-side writes over WebSocket (see proposal non-goals).
- Solving production deployment on PythonAnywhere (flagged as a risk,
  not solved — see Risks).
- Migrating `django-user-visit` or any other unrelated
  request-response middleware to async.

## Decisions

### D1: Push-only WebSocket; all writes stay on HTTP
Already the proposal's core scoping call — restated here because it's
the decision every other design choice depends on. Consumers only
need `receive` handling for the initial group-join (Channels wires
this via `channel_layer.group_add` in `connect()`), not for
arbitrary client messages. This keeps `apps/main/services.py` as the
single source of truth for validation/permissions, so the 45-test
existing suite's coverage of those functions remains fully
applicable — no parallel permission logic to keep in sync in the
consumers.

### D2: Broadcast from `services.py`, not via Django signals
Alternative considered: use `post_save` signals on `Notification`/
`ConversationMessages` to trigger the broadcast, decoupling
services.py from Channels entirely. Rejected — signals are harder to
trace (an implicit side effect of `.save()`, not visible at the call
site) and this project doesn't use signals anywhere else; an explicit
`channel_layer.group_send(...)` call at the end of
`create_notification`/`post_conversation_message` is more consistent
with this codebase's existing explicit style and easier to test
directly.

### D3: Per-user group for notifications, per-application group for chat — one connection joins both
- Notifications: group name `notifications_{userprofile.id}` — one
  group per recipient, joined in `connect()` after confirming
  `request.user.is_authenticated` and a `UserProfile` exists (mirrors
  the existing `dashboard` view's
  `UserProfile.objects.filter(user=request.user).exists()` check).
- Chat: group name `chat_{application_id}` — joined after replicating
  `viewApplication`'s ownership check (query the `Application`
  directly rather than importing the view, to avoid pulling
  HTTP-request-shaped code into a WebSocket consumer).
- **Revised after initial implementation**: rather than two separate
  consumer classes on two separate URLs (`/ws/notifications/` and
  `/ws/chat/<id>/`), both are merged into a single `RealtimeConsumer`
  reachable at `/ws/updates/` (notifications only) or
  `/ws/updates/<application_id>/` (notifications + that application's
  chat, since the application-detail page needs both). Every
  connection always joins its own notifications group; it
  additionally joins a chat group only when opened with an
  `application_id`. This means the application-detail page opens one
  physical WebSocket instead of two (its own chat connection plus
  `main.js`'s page-wide notifications connection) — `main.js` checks a
  `window.__mergedRealtimeSocket` flag the chat page sets first and
  skips opening its own redundant connection. Outgoing payloads now
  carry a `"kind"` field (`"notification"` or `"chat"`) so the client
  can dispatch a single `onmessage` handler correctly.

### D4: Daphne as the ASGI server, added to `INSTALLED_APPS`
Django Channels' documented setup: add `"daphne"` as the *first* app
in `INSTALLED_APPS` (before `django.contrib.staticfiles`), which lets
`manage.py runserver` itself serve ASGI/WebSocket in dev — no
separate dev command needed. For the Docker image, switch the
`docker-compose.yml` `web` command to `daphne -b 0.0.0.0 -p 9000
jobPortal.asgi:application` explicitly, since relying on
`runserver`'s dev-only ASGI shim in a container is not the documented
production path.

Alternative considered: Uvicorn instead of Daphne. Rejected — Daphne
is Channels' own reference server and the one whose `runserver`
integration is documented; no reason to introduce a second ASGI
runtime to evaluate.

### D5: Redis as the channel layer backend
`channels-redis` is the standard production-grade channel layer
(the in-memory layer is explicitly single-process/dev-only and
wouldn't work with more than one Daphne worker). Add a `redis`
service to `docker-compose.yml` (official `redis:7-alpine` image, no
persistence needed — channel layer messages are transient).

## Risks / Trade-offs

- **PythonAnywhere doesn't support long-lived WebSocket connections**
  on its free/standard web-app tiers (confirmed against their hosting
  model — only their "Always-on tasks" / paid tiers offer raw socket
  support, and even then not as a drop-in for their WSGI-based web app
  product). This change delivers real-time in Docker/local dev but
  **not** on the project's current stated production host. → This is
  a genuine decision point for the user: either accept
  local-dev-only real-time for now, or move production off
  PythonAnywhere as a related decision. Not resolved here — flagged
  for the user to decide before `/opsx:apply`.
- **New moving parts**: Redis is a new runtime dependency the project
  didn't have before (Postgres and S3 were already optional/toggled;
  Redis becomes required once Channels is wired in, even in dev).
  → Mitigation: containerized via `docker-compose.yml`, no manual
  install step for anyone using Docker; document the local
  non-Docker dev path (task 5) for anyone still using `uv run
  runserver` directly.
- **Testing pattern split**: existing tests are Django `TestCase`
  (synchronous, WSGI-style); consumer tests need
  `channels.testing.WebsocketCommunicator` (async). → Isolated to a
  new `apps/main/tests/test_consumers.py`; doesn't touch the existing
  45 tests.
- **Connections didn't stay alive indefinitely** (found during manual
  verification, not anticipated here): a `redis.exceptions.TimeoutError`
  disconnected idle WebSockets after ~5s of no traffic. Root-caused,
  not just band-aided: `channels_redis.core.RedisChannelLayer`'s
  internal blocking receive (`brpop_timeout`) defaults to 5s, and
  `redis-py` 8.x (installed here) changed its own default socket read
  timeout to 5s too — the two race, and the socket-level timeout wins
  on an idle connection, which `channels` does not retry (it
  disconnects). Fixed by passing explicit `socket_timeout=20`/
  `socket_connect_timeout=5` in `CHANNEL_LAYERS`' Redis host config —
  confirmed by holding a connection idle past the old 5s window with
  the fix in place (8s, no crash) and by re-running the full consumer
  test suite against a live Redis. Client-side reconnect-on-close
  (fixed 3s backoff, no exponential backoff/jitter) is kept as
  defense-in-depth regardless — any long-lived WebSocket client should
  have it independent of this specific fix.
- **Static files don't hot-reload in this project's Docker setup**:
  `jobPortal/urls.py` serves static assets from `STATIC_ROOT` (the
  `collectstatic`-collected copy), not the live `static/` source — a
  pre-existing convention, not introduced here. Every JS change in
  this rollout needed `manage.py collectstatic` re-run before it took
  effect in the running container; easy to miss.

## Migration Plan

1. Add `channels`, `channels-redis`, `daphne` dependencies.
2. Add `"daphne"` to `INSTALLED_APPS` (first entry), `CHANNEL_LAYERS`
   pointing at Redis, wire `jobPortal/asgi.py`'s
   `ProtocolTypeRouter`/`AuthMiddlewareStack`.
3. Add `apps/main/consumers.py` (`NotificationConsumer`,
   `ChatConsumer`) + `apps/main/routing.py`.
4. Add `group_send` calls to `apps/main/services.py`'s
   `create_notification` and `post_conversation_message`.
5. Add `redis` service to `docker-compose.yml`; switch `web`'s
   command to Daphne.
6. Replace the JS polling (`static/js/main.js`,
   `view-application-job.html`) with a WebSocket client.
7. Add consumer tests using `WebsocketCommunicator`.
8. Run the full existing test suite (must still pass unmodified) plus
   the new consumer tests; verify manually in Docker with two browser
   sessions (one per participant) that a chat message sent by one
   appears in the other without a page reload.

Rollback: revert the commit(s). No data migration (no new models),
but `docker-compose.yml`'s new `redis` service and changed `web`
command would need reverting too for local dev to go back to the
previous state.

## Open Questions

None — resolved: this change targets Docker/local dev only. No
polling-fallback logic is built for PythonAnywhere; production hosting
is a separate decision to revisit later if real-time there becomes a
priority.
