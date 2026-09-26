# Proposal

## Why

Same rationale as `extract-main-services-and-cleanup` (Phase 1),
applied to `accounts/views.py`: profile/education/mobile-number/
password logic (`createUserProfile`, `updateUserPeofile`,
`createEducation`, `updateEducation`, `createMobileNumber`,
`updateMobileNumber`, `deleteMobileNumber`, `change_password`) is
mixed directly into view functions. This change should not start
until Phase 1 has shipped and proven the extraction pattern works
without regressions.

## What Changes

- Add `accounts/services.py`, extract the ORM-mutating logic from the
  8 views listed above (views keep permission checks,
  request/response handling, and call into services).
- **No behavior change** — `accounts/tests/test_profile.py` (14 tests)
  must pass unmodified.

### Explicit non-goals
- `register`/`login`/`logout`/`activate` — these are thin enough
  (mostly Django auth calls) that extracting them adds indirection
  without much benefit; only extract if they grow.
- Anything touched in Phase 1 (`main` app) — separate, already done.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
None — pure internal restructuring, no spec-level behavior change.
`skip_specs: true` is set in `.openspec.yaml`.

## Impact

- New file: `accounts/services.py`
- Modified: `accounts/views.py` (thinner)
- No template, URL, or migration changes.
- Existing 18 accounts tests must pass unmodified.
