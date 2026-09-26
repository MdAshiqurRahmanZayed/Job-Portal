# Spec Delta

## Purpose

Automated test coverage for the account registration/auth flow, job
posting/application flow, and the chat API — the highest-traffic,
highest-risk paths in the application — enforced on every PR.

## ADDED Requirements

### Requirement: Account registration is covered
Automated tests SHALL verify that registration succeeds with valid
input and is rejected with invalid or duplicate input.

#### Scenario: Valid registration succeeds
- **WHEN** a registration test submits a unique email and valid
  required fields
- **THEN** an `Account` is created and the response indicates success

#### Scenario: Duplicate email is rejected
- **WHEN** a registration test submits an email already used by an
  existing `Account`
- **THEN** no second account is created and the response indicates the
  error

### Requirement: Login and logout are covered
Automated tests SHALL verify that login succeeds only with correct
credentials, and that logout ends the session.

#### Scenario: Valid credentials log in
- **WHEN** a login test submits the correct email and password for an
  existing account
- **THEN** the request succeeds and the session is authenticated

#### Scenario: Invalid credentials are rejected
- **WHEN** a login test submits an incorrect password
- **THEN** the request fails and no session is authenticated

### Requirement: Profile onboarding is covered
Automated tests SHALL verify that profile, education, and mobile-number
creation/update/delete require authentication and persist correctly
for the authenticated user.

#### Scenario: Authenticated profile creation persists
- **WHEN** an authenticated user submits valid profile data
- **THEN** a `UserProfile` is created/updated for that user

#### Scenario: Unauthenticated profile action is rejected
- **WHEN** a profile, education, or mobile-number create/update/delete
  request is made without an authenticated session
- **THEN** the request is redirected to login and no record is
  created, changed, or removed

#### Scenario: Mobile number delete removes the record
- **WHEN** an authenticated user deletes their own `mobileNumber`
  record
- **THEN** the record no longer exists

### Requirement: Job create/update/delete permission checks are covered
Automated tests SHALL verify that only an authenticated user can
create a job, and that only a job's creator can update or delete it.

#### Scenario: Unauthenticated create is rejected
- **WHEN** a create-job test request is made without an authenticated
  session
- **THEN** the request is redirected to login and no `Job` is created

#### Scenario: Non-owner cannot update or delete
- **WHEN** an authenticated user who did not create a `Job` attempts to
  update or delete it
- **THEN** the request is rejected and the `Job` is unchanged

#### Scenario: Owner can update and delete
- **WHEN** the authenticated user who created a `Job` updates or
  deletes it
- **THEN** the change is persisted (update) or the `Job` no longer
  exists (delete)

### Requirement: Job listing and detail views are covered
Automated tests SHALL verify that job listing and job detail views
return the expected jobs.

#### Scenario: Listing returns existing jobs
- **WHEN** a test requests the job listing view with existing `Job`
  records
- **THEN** the response includes those jobs

#### Scenario: Detail view returns the requested job
- **WHEN** a test requests the job detail view for an existing `Job`
- **THEN** the response contains that job's data

### Requirement: Job category filtering, search, and "my created jobs" are covered
Automated tests SHALL verify category-filtered job listing, job search,
and the authenticated "my created jobs" view.

#### Scenario: Category filter returns only matching jobs
- **WHEN** a test requests jobs filtered by an existing `Category`
- **THEN** the response includes only jobs in that category

#### Scenario: Search returns matching jobs
- **WHEN** a test searches using a term matching an existing job's
  title or description
- **THEN** the response includes that job

#### Scenario: "My created jobs" returns only the requesting user's jobs
- **WHEN** an authenticated user requests their created-jobs view
- **THEN** the response includes only jobs they created, not other
  users' jobs

### Requirement: Application submission and permission checks are covered
Automated tests SHALL verify that an authenticated user can submit an
application to a job, and that only the applicant or the job's owner
can view or delete that application.

#### Scenario: Authenticated user submits an application
- **WHEN** an authenticated user submits an application to an existing
  `Job`
- **THEN** an `Application` record is created linking that user and job

#### Scenario: Unrelated user cannot view or delete an application
- **WHEN** a user who is neither the applicant nor the job's owner
  requests to view or delete an `Application`
- **THEN** the request is rejected

#### Scenario: Applicant sees only their own applications
- **WHEN** an authenticated user requests their applications-list view
- **THEN** the response includes only `Application` records they
  submitted

#### Scenario: Job owner sees applicants for their job
- **WHEN** a job's creator requests the applicants view for that job
- **THEN** the response includes the applications submitted to that
  job

#### Scenario: Non-owner cannot view a job's applicants
- **WHEN** a user who did not create the job requests its applicants
  view
- **THEN** the request is rejected

### Requirement: Chat API is covered
Automated tests SHALL verify the chat API's read and write behavior.

#### Scenario: Authenticated GET returns messages
- **WHEN** an authenticated request is made to
  `ChatMessageAPIView`/`apiConversion` for an existing conversation
- **THEN** the response contains the expected `ConversationMessages`
  data

#### Scenario: Authenticated POST creates a message
- **WHEN** an authenticated request posts a new chat message with
  valid data
- **THEN** a `ConversationMessages` record is created and returned

#### Scenario: Invalid POST is rejected
- **WHEN** a request posts invalid or missing required chat message
  data
- **THEN** the request is rejected with an error response and no
  record is created

### Requirement: Tests run in CI on every pull request
CI SHALL run the automated test suite on every pull request, so
regressions in these flows are caught before merge.

#### Scenario: CI fails on a broken test
- **WHEN** a pull request introduces a change that breaks one of the
  covered flows
- **THEN** the CI test job fails and blocks a green check
