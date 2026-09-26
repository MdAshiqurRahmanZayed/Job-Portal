# Tasks

## 1. Extract profile/education/mobile-number services

- [x] 1.1 Create `accounts/services.py` with `create_profile(account, form) -> UserProfile`, `update_profile(profile, form) -> UserProfile`; update `createUserProfile`/`updateUserPeofile` to call them; verify `uv run python manage.py test accounts.tests.test_profile.ProfileTests` passes unmodified
- [x] 1.2 Add `create_education(profile, form) -> Education`, `update_education(education, form) -> Education`; update `createEducation`/`updateEducation`; verify `uv run python manage.py test accounts.tests.test_profile.EducationTests` passes unmodified — note: `createEducation` sets `userprofile.education = True` on a field that doesn't exist on `UserProfile` (pre-existing no-op); preserved byte-for-byte inside the service rather than silently dropped
- [x] 1.3 Add `create_mobile_number(profile, form) -> mobileNumber`, `update_mobile_number(mobile, form) -> mobileNumber`, `delete_mobile_number(mobile) -> None`; update `createMobileNumber`/`updateMobileNumber`/`deleteMobileNumber`; verify `uv run python manage.py test accounts.tests.test_profile.MobileNumberTests` passes unmodified

## 2. Extract change-password service

- [x] 2.1 Add `change_user_password(account, current_password, new_password) -> bool` (returns whether the current password check succeeded) to `accounts/services.py`; update `change_password` view to call it; verify `uv run python manage.py test accounts.tests.test_profile.ChangePasswordTests` passes unmodified

## 3. Full verification

- [x] 3.1 Run `uv run python manage.py test accounts` — verify all 18 accounts tests still pass unmodified
- [x] 3.2 Run `ruff check .` and `ruff format .` — verify clean
