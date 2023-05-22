from django.urls import path,include
from .views import *

urlpatterns = [
    path('register/',register,name='register'),
    path('login/',login,name='login'),
    path('logout/',logout,name='logout'),
    path('change-password/', change_password, name='change_password'),
    path('create-user-profile/', createUserProfile, name='createUserProfile'),
    path('update-user-profile/', updateUserPeofile, name='updateUserPeofile'),
    
    path('dashboard/',dashboard,name='dashboard'),
    
    
    
    
    #Education
    path('create-education/',createEducation,name='createEducation'),
    path('update-education/',updateEducation,name='updateEducation'),
]
