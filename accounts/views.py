from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib import messages,auth
from django.contrib.auth.decorators  import login_required
from main.models import Job,Application
from django.core import serializers
from .forms import *
from django.conf import settings
from accounts.models import *
# Create your views here.

def register(request):
     if request.method == "POST":
          try:
               form = RegistrationForm(request.POST)
               # user_test = Account.objects.filter(email=email).exists()
               # print(form)

               if form.is_valid():
                         email = form.cleaned_data['email']
                         password = form.cleaned_data['password']
                         username = email.split("@")[0]
                         
                         user = Account.objects.create_user(email=email, username=username, password=password)
                         user.save()
                         
                         return redirect('login')
                         
          except:
                         messages.warning(request,'Check email and password')
                         return redirect('register')
     else:
          form =  RegistrationForm()
     
     context = {
          'form':form
     }
     
     return render(request,'accounts/register.html',context)

def login(request):
     if request.method == "POST":
          email = request.POST['email']
          password = request.POST['password']
          user = auth.authenticate( email=email, password=password)
          if user is not None:
               auth.login(request,user)
               messages.success(request, 'You are successfully logged in.')
               return redirect('dashboard')
          else:
               messages.warning(request, 'Bad cradentials.')
               return redirect('login')
          
     return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
     auth.logout(request)
     messages.success(request, 'You are logged out.')
     return redirect('login')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.warning(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.warning(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url = 'login')
def dashboard(request):
     # try:
     #      # UserProfile.objects.get(user__id=request.user.id):
     #      print('das')
     #      userprofile          = UserProfile.objects.filter(user=request.user).exists()
     #      createdJob           = Job.objects.filter(user = userprofile).count()
     #      createdApplicantion  = Application.objects.filter(user = request.user.userprofile).count()
     #      totalApplicant       = Application.objects.filter( job__user = request.user.userprofile).count()
     # except:

     if UserProfile.objects.filter(user=request.user).exists() == True:
          userprofile          = UserProfile.objects.get(user=request.user)
          createdJob           = Job.objects.filter(user = userprofile).count()
          createdApplicantion  = Application.objects.filter(user = request.user.userprofile).count()
          totalApplicant       = Application.objects.filter( job__user = request.user.userprofile).count()
     else:
          userprofile = "Please Complete Your Profile"
          createdJob = "0"
          totalApplicant = "0"
          createdApplicantion = "0"
               
          
     context = {
          'userprofile':userprofile,
          'createdJob':createdJob,
          'createdApplicantion':createdApplicantion,
          'totalApplicant':totalApplicant,
     } 
     
     
     
     return render(request,'accounts/dashboard.html',context)
# @login_required(login_url = 'login')
# def dashboard(request):
#      if UserProfile.objects.filter(user__id = request.user.id).exists():
#           userprofile          = UserProfile.objects.get(user = request.user)
#           createdJob           = Job.objects.filter(user = userprofile).count()
#           createdApplicantion  = Application.objects.filter(user = request.user.userprofile).count()
#           totalApplicant       = Application.objects.filter( job__user = request.user.userprofile).count()
#      else:
#           userprofile = "Please Complete Your Profile"
#           createdJob = "0"
#           totalApplicant = "0"
#           createdApplicantion = "0"
          
#      context = {
#           'userprofile':userprofile,
#           'createdJob':createdJob,
#           'createdApplicantion':createdApplicantion,
#           'totalApplicant':totalApplicant,
#      } 
     
#      return render(request,'accounts/dashboard.html',context)


@login_required(login_url='login')
def createUserProfile(request):
     if UserProfile.objects.filter(user__email = request.user.email).exists():
          messages.warning(request,"Already created Profile")
          return redirect('dashboard')
     else:
          if request.method == "POST":
               profile_form = createProfile(request.POST,request.FILES)
               user = request.user
               if profile_form.is_valid():
                    
                    profile =  profile_form.save( commit=False)
                    profile.user = user 
                    print(profile)
                    profile.save()  
                    messages.success(request, 'Your profile has been created successfully.')
                    return redirect('updateUserPeofile')
          else:
               profile_form = createProfile()
          context = {
               'profile_form':profile_form
          }
     return render(request,'accounts/create_profile.html',context)


@login_required(login_url='login')
def updateUserPeofile(request):
     userProfile = get_object_or_404(UserProfile,user = request.user)
     # phone_numbers = userProfile.phone_number.split(',')
     
     mobile_numbers = mobileNumber.objects.filter(userprofile = request.user.userprofile)
     
     if request.method == "POST":
          try:
               profile_form = updateProfile(request.POST, request.FILES, instance=userProfile)
               if profile_form.is_valid():
                    profile_form.save()
                    messages.success(request, 'Your profile has been updated successfully.')
                    return redirect('updateUserPeofile')
          except:
                    messages.warning(request, 'Your profile has not been updated.')
                    return redirect('updateUserPeofile')
               
     else:
          profile_form = updateProfile(instance = userProfile)
     context ={
          'profile_form':profile_form,
          # 'phone_numbers': phone_numbers,
          'mobile_numbers': mobile_numbers,
     }
     return render(request,'accounts/create_profile.html',context)
     
def showUserProfile(request,id):
     userprofile = UserProfile.objects.get(id=id)
     
     print(request.user.userprofile.role)
     if userprofile.role == 'jobseeker':
          educations   = Education.objects.get(user=userprofile)
          context = {
         'userprofile': userprofile,
         'education_fields': educations.__dict__,
         'MEDIA_URL': settings.MEDIA_URL,  # Include MEDIA_URL in the context
         }
     else:
          educations   =None
          context = {
         'userprofile': userprofile,
     #     'education_fields': educations.__dict__,
         'MEDIA_URL': settings.MEDIA_URL,  # Include MEDIA_URL in the context
         }
          
     
     return render(request,'accounts/profile.html',context)
     
     
     
     
#Education
@login_required(login_url='login')
def createEducation(request):
     if request.user.userprofile.role == "employer":
          messages.warning(request, 'You are not allowed.')
          return redirect('dashboard')
     if request.method == "POST":
          try:
               form = educationForm(request.POST)  
               if form.is_valid():
                    form = form.save(commit=False)
                    form.user = request.user.userprofile
                    form.save() 
                    userprofile = UserProfile.objects.get(user = request.user)
                    userprofile.education = True
                    userprofile.save()
                    messages.success(request, 'Your Education has been Created successfully.')
                    return redirect('updateEducation')
          except:
                    messages.warning(request, 'Your Education has been not Created.')
                    return redirect('dashboard')
     else:
          form = educationForm()  
               
     context = {
          "form":form
     }
     
     return render(request,'main/create-education.html',context)


@login_required(login_url = 'login')
def updateEducation(request):
     if request.user.userprofile.role == "employer":
               messages.warning(request, 'You are not allowed.')
               return redirect('dashboard')
     education = Education.objects.get(user = request.user.userprofile)
     if request.method == "POST":
               
          form = educationForm(request.POST,request.FILES ,instance = education ) 
          try:
               if form.is_valid():
                    form = form.save(commit=False)
                    form.save()
                    messages.success(request, 'Your Education has been updated successfully.')
                    return redirect('updateEducation')
          except:
                    messages.warning(request, 'Your Education has been not updated.')
                    return redirect('dashboard')
     else:
          form = educationForm(instance = education)
     context = {
          'form':form
     }
     return render(request,'main/create-education.html',context)
 
 
@login_required(login_url='login')
def createMobileNumber(request):

     if request.method == "POST":
          try:
               form = mobileNumberForm(request.POST)  
               print(form)
               if form.is_valid():
                    form = form.save(commit=False)
                    form.userprofile = request.user.userprofile
                    form.save()
                    messages.success(request, 'Your Mobile Number has been Created successfully.')
                    return redirect('updateUserPeofile')
          except:
                    messages.warning(request, 'Your Mobile Number has not been Created.')
                    return redirect('createMobileNumber')
     else:
         form = mobileNumberForm()
               
     context = {
          "form":form
     }
     
     return render(request,'accounts/create-mobile-number.html',context)

@login_required(login_url='login')
def updateMobileNumber(request,pk):
     mobile_number = mobileNumber.objects.get(id=pk)
     if request.method == "POST":
          try:
               form = mobileNumberForm(request.POST,instance=mobile_number)  
               print(form)
               if form.is_valid():
                    form = form.save(commit=False)
                    form.save()
                    messages.success(request, 'Your Mobile Number has been Updated successfully.')
                    return redirect('updateUserPeofile')
          except:
                    messages.warning(request, 'Your Mobile Number has not been Updated.')
                    return redirect('updateUserPeofile')
     else:
         form = mobileNumberForm(instance=mobile_number)
               
     context = {
          "form":form
     }
     
     return render(request,'accounts/create-mobile-number.html',context)


@login_required(login_url='login')
def deleteMobileNumber(request,pk):
     mobile_number = mobileNumber.objects.get(id=pk)
     try:
               mobile_number.delete()
               messages.success(request, 'Your Mobile Number has been Deleted successfully.')
               return redirect('updateUserPeofile')
     except:
               messages.warning(request, 'Your Mobile Number has not been Deleted.')
               return redirect('updateUserPeofile')
               
     
     
