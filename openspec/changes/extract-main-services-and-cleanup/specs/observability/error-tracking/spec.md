# Spec Delta

## Purpose

Ensures unhandled exceptions in production are captured and reported
(Sentry) instead of disappearing into console output, with basic
logging as a fallback when Sentry isn't configured.

## ADDED Requirements

### Requirement: Unhandled exceptions are reported to Sentry when configured
The application SHALL initialize Sentry error tracking when a
`SENTRY_DSN` environment variable is set, capturing unhandled
exceptions raised during request handling.

#### Scenario: Sentry configured and an unhandled exception occurs
- **WHEN** `SENTRY_DSN` is set and a view raises an unhandled exception
- **THEN** the exception is reported to Sentry

#### Scenario: Sentry not configured
- **WHEN** `SENTRY_DSN` is unset (e.g. local development)
- **THEN** the application starts normally with no Sentry calls
  attempted and no error raised by the absence of the DSN

### Requirement: Basic logging configuration exists
The project SHALL define a Django `LOGGING` configuration so
unhandled exceptions and at least warning-level messages are visible
in console/server logs regardless of whether Sentry is configured.

#### Scenario: Exception is logged
- **WHEN** an unhandled exception occurs during request handling
- **THEN** it appears in the configured log output
