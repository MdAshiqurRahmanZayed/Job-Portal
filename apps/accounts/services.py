from .models import Account, Education, UserProfile, mobileNumber


def create_profile(account: Account, form) -> UserProfile:
    profile = form.save(commit=False)
    profile.user = account
    profile.save()
    return profile


def update_profile(profile: UserProfile, form) -> UserProfile:
    profile = form.save(commit=False)
    profile.save()
    return profile


def create_education(profile: UserProfile, form) -> Education:
    education = form.save(commit=False)
    education.user = profile
    education.save()
    # Note: `education` is not a real UserProfile field; this assignment is a
    # pre-existing no-op preserved as-is (see extract-accounts-services change).
    profile.education = True
    profile.save()
    return education


def update_education(education: Education, form) -> Education:
    education = form.save(commit=False)
    education.save()
    return education


def create_mobile_number(profile: UserProfile, form) -> mobileNumber:
    mobile = form.save(commit=False)
    mobile.userprofile = profile
    mobile.save()
    return mobile


def update_mobile_number(mobile: mobileNumber, form) -> mobileNumber:
    mobile = form.save(commit=False)
    mobile.save()
    return mobile


def delete_mobile_number(mobile: mobileNumber) -> None:
    mobile.delete()


def change_user_password(
    account: Account, current_password: str, new_password: str
) -> bool:
    if not account.check_password(current_password):
        return False
    account.set_password(new_password)
    account.save()
    return True
