from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('all-jobs/',allJobs,name='allJobs'),
    path('search/', searchJobs, name="searchJobs"),
    path('job-detail/<str:slug>/<int:pk>/',jobDetail,name='jobDetail'),
    path('my-created-job/',myCreatedJobs,name='myCreatedJobs'),
    path('create-job/',createJob,name='createJob'),
    path('update-job/<int:pk>/',updateJob,name='updateJob'),
    path('delete-job/<int:pk>/',deleteJob,name='deleteJob'),
    
    #application
    path('create-application-for-job/<int:pk>/',createApplication,name='createApplication'),
    path('all-application/',allApplication,name='allApplication'),
    path('view-application/<int:pk>/',viewApplication,name='viewApplication'),
    path('delete-application/<int:pk>/',deleteApplication,name='deleteApplication'),
    
    path('all-applicant/<int:pk>/',allApplicant,name='allApplicant'),
    
    #notification
    path('notifications/', notifications, name='notifications'),
    path('send-messages/<int:pk>/', sendMessages, name='sendMessages'),
    

]
