from django.urls import path

from .views import (
    activate,
    change_password,
    createEducation,
    createMobileNumber,
    createUserProfile,
    dashboard,
    deleteMobileNumber,
    login,
    logout,
    register,
    showUserProfile,
    updateEducation,
    updateMobileNumber,
    updateUserPeofile,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("change-password/", change_password, name="change_password"),
    path("dashboard/", dashboard, name="dashboard"),
    # Activate by email
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    # profile
    path("profile/<int:id>", showUserProfile, name="showUserProfile"),
    path("create-user-profile/", createUserProfile, name="createUserProfile"),
    path("update-user-profile/", updateUserPeofile, name="updateUserPeofile"),
    # mobile number
    path("create-mobile-number/", createMobileNumber, name="createMobileNumber"),
    path(
        "update-mobile-number/<int:pk>/", updateMobileNumber, name="updateMobileNumber"
    ),
    path(
        "delete-mobile-number/<int:pk>/", deleteMobileNumber, name="deleteMobileNumber"
    ),
    # Education
    path("create-education/", createEducation, name="createEducation"),
    path("update-education/", updateEducation, name="updateEducation"),
]
