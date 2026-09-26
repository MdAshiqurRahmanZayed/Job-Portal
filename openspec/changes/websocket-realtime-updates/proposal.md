# Proposal

## Why

Notifications and chat currently update via aggressive client-side
polling instead of any real push mechanism:
- `static/js/main.js`'s `updateNotificationsCount()` polls
  `/notifications-count/` every **2 seconds**, on every page, for
  every logged-in tab open.
- `templates/main/view-application-job.html`'s `fetchMessages()`
  polls the chat API every **1 second** while an application's chat
  view is open.
- A second notification-polling function,
  `updateNotificationsCountOther`, is called as
  `setInterval(updateNotificationsCountOther(number), 2000)` — this
  invokes the function immediately and passes its (undefined) return
  value to `setInterval`, so on the application-detail page it only
  ever polls once, not repeatedly. A real bug, found while grounding
  this proposal.
- `apps/main/context_processors.py`'s `notifications()` context
  processor also runs 2 extra queries on **every single page
  render**, site-wide, regardless of whether that page shows
  notifications.

This is expensive (constant server load per open tab) and not
actually real-time (up to 1-2s of staleness, worse under load). This
change replaces the polling with WebSocket push for both notifications
and chat messages.

## What Changes

- Add Django Channels + a Redis channel layer; introduce
  `jobPortal/asgi.py` as the real entrypoint (already scaffolded,
  currently unused) via `ProtocolTypeRouter` +
  `AuthMiddlewareStack` (reuses existing session auth — no new auth
  mechanism needed).
- Add two consumers under `apps/main/consumers.py`:
  - `NotificationConsumer` — one WebSocket per authenticated user,
    joins a per-user channel group, pushes new `Notification` events.
  - `ChatConsumer` — one WebSocket per open application chat view,
    joins a per-application channel group (only the applicant or the
    job's owner may join — mirrors `viewApplication`'s existing
    permission check), pushes new `ConversationMessages` events.
- **Push-only over WebSocket; all writes stay on existing HTTP
  paths.** `apps/main/services.py`'s `create_notification` and
  `post_conversation_message` are the two existing choke points for
  all notification/message creation (already used by
  `submit_application`, `viewApplication`'s POST branch). Add a
  `channel_layer.group_send(...)` call at the end of each — no new
  validation/permission logic duplicated in the consumers, and the
  existing 45-test suite's coverage of those code paths keeps
  applying unchanged.
- Remove the JS polling: `static/js/main.js`'s
  `updateNotificationsCount`/`updateNotificationsCountOther` and their
  `setInterval` calls, and `view-application-job.html`'s
  `setInterval(fetchMessages, 1000)`. Replace with a small WebSocket
  client script that opens a connection and updates the DOM on
  incoming pushes, using the existing initial-load HTTP endpoints
  (`/notifications-count/`, `ChatMessageAPIView` GET) for the first
  render before the socket takes over.
- Docker: add a `redis` service to `docker-compose.yml` (Channels'
  channel layer backend); switch the `web` service's command from
  `python manage.py runserver` to an ASGI server (Daphne) so
  WebSocket connections are actually served.

### Explicit non-goals

- Moving message/notification **creation** onto the WebSocket
  connection (client → server writes) — out of scope; keeps one
  validated write path instead of two.
- Typing indicators, read receipts beyond the existing `is_seen`
  flag, or any new real-time feature beyond replacing polling.
- Production ASGI deployment beyond Docker/Daphne (e.g. a
  reverse-proxy WebSocket-upgrade config for a specific host) — the
  project's only known deployment target right now is PythonAnywhere,
  which does not support persistent WebSocket connections on its
  free/standard tiers; this is flagged as a real deployment risk in
  design.md, not solved here.

## Capabilities

### New Capabilities
- `realtime/notifications-and-chat`: notifications and chat messages
  are pushed to connected clients over WebSocket instead of requiring
  the client to poll for them.

### Modified Capabilities
None.

## Impact

- New: `apps/main/consumers.py`, `apps/main/routing.py`, Redis service
  in `docker-compose.yml`, a small WebSocket client JS file
- Modified: `jobPortal/asgi.py` (routing wired in), `jobPortal/settings`
  (`CHANNEL_LAYERS`, `INSTALLED_APPS` += `channels`/`daphne`),
  `apps/main/services.py` (group_send calls added to 2 functions),
  `pyproject.toml`/`uv.lock` (+`channels`, `channels-redis`, `daphne`),
  `Dockerfile`/`docker-compose.yml` (ASGI server + redis service),
  `static/js/main.js`, `templates/main/view-application-job.html`,
  `templates/includes/navbar.html`
- New test pattern: Channels' `WebsocketCommunicator`-based tests,
  alongside (not replacing) the existing Django `TestCase` suite.
- **Deployment risk**: production currently targets PythonAnywhere,
  which doesn't support long-lived WebSocket connections on standard
  tiers — this change makes local/Docker real-time, but the
  production site would need a different host (or fall back to
  polling there) to actually benefit. Flagged for the user to decide,
  not resolved by this change.
