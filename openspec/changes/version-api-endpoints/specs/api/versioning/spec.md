# Spec Delta

## Purpose

Defines that the project's DRF API endpoints live under a versioned
`api/v1/` prefix, so future breaking API changes can ship as `v2`
without disrupting existing callers, and that callers use relative
URLs rather than a hardcoded origin.

## ADDED Requirements

### Requirement: DRF endpoints are served under a versioned prefix
All DRF API endpoints SHALL be served under `api/v1/` rather than a
bare `api/` prefix.

#### Scenario: Conversion endpoint resolves under v1
- **WHEN** a request is made to `api/v1/conversion/`
- **THEN** the `apiConversion` viewset handles it

#### Scenario: Chat endpoint resolves under v1
- **WHEN** a request is made to `api/v1/chat-messages/<id>/`
- **THEN** `ChatMessageAPIView` handles it

#### Scenario: Old unversioned path no longer resolves
- **WHEN** a request is made to the old `api/conversion/` or
  `api/chat-messages/<id>/` path
- **THEN** it returns 404 (no route registered there any more)

### Requirement: Client-side API calls use relative URLs
Templates and client-side scripts calling these endpoints SHALL use a
relative path, not a hardcoded scheme+host+port.

#### Scenario: Chat fetch uses a relative path
- **WHEN** `view-application-job.html`'s chat-related `fetch()` calls
  are inspected
- **THEN** neither hardcodes `http://127.0.0.1:8000` or any other
  absolute origin
