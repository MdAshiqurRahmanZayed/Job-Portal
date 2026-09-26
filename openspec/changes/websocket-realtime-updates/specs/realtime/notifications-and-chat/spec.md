# Spec Delta

## Purpose

Notifications and chat messages are pushed to connected clients over
WebSocket as they're created, instead of requiring the client to poll
an HTTP endpoint on a fixed interval.

## ADDED Requirements

### Requirement: Authenticated users receive notifications in real time
An authenticated user with an open WebSocket connection SHALL receive
a push event when a new `Notification` is created for them, without
polling.

#### Scenario: New notification pushed to the recipient
- **WHEN** a `Notification` is created with `to_user` set to a
  connected user's profile
- **THEN** that user's open WebSocket connection receives an event
  describing the new notification

#### Scenario: Unauthenticated connection is rejected
- **WHEN** a WebSocket connection to the notifications endpoint is
  attempted without an authenticated session
- **THEN** the connection is rejected

### Requirement: Chat participants receive new messages in real time
A connected user viewing an application's chat SHALL receive a push
event when a new `ConversationMessages` is created for that
application, without polling — but only if they are the applicant or
the job's owner.

#### Scenario: New message pushed to both participants
- **WHEN** a `ConversationMessages` is created for an `Application`
- **THEN** both the applicant's and the job owner's open WebSocket
  connections for that application receive an event with the new
  message

#### Scenario: Unrelated user cannot join the chat channel
- **WHEN** a user who is neither the applicant nor the job's owner
  attempts to open a WebSocket connection for that application's chat
- **THEN** the connection is rejected

### Requirement: Message and notification creation stays on existing HTTP paths
Creating a notification or chat message SHALL continue to go through
the existing, permission-checked HTTP views and `apps/main/services.py`
functions. WebSocket connections SHALL NOT accept client-submitted
messages or notifications.

#### Scenario: Consumer receives no inbound write
- **WHEN** a client sends arbitrary data over an open
  `NotificationConsumer` or `ChatConsumer` WebSocket connection
- **THEN** no `Notification` or `ConversationMessages` record is
  created as a result — creation only happens via the existing HTTP
  views
