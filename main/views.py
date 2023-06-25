from rest_framework.views import APIView
from .serializers import ChatMessageSerializer
# from .models import ChatMessage
from rest_framework.response import Response
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import auth,messages
from main.utilities import create_notification
from django.http import JsonResponse 
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from mptt.templatetags.mptt_tags import tree_info
from django.db.models import Q
from rest_framework import viewsets, views

# Create your views here.
def home(request):
     testimonials = Review.objects.filter(show = True) 
     jobs = Job.objects.filter(is_published=True).order_by('-id')[:3]
          
     context = {
          "jobs":jobs,
          "testimonials": testimonials,
     }
     return render(request,'home.html',context)


def allJobs(request):
    jobs = Job.objects.filter(is_published=True).order_by('-id')
    jobs_count = Job.objects.filter(is_published=True).count()
#     top_jobs = Job.objects.filter(top_course=True)
    categories = Category.objects.all()

    #pagination
    paginator = Paginator(jobs, 5)
    page = request.GET.get('page')
    pagedJobs = paginator.get_page(page)

    context = {
        "jobs": pagedJobs,
        "jobs_count": jobs_count,
     #    "top_jobs": top_jobs,
        "categories": categories,
        'tree_info': tree_info(categories),
    }
    return render(request, 'main/all-jobs.html', context)


def searchJobs(request):
    if 'keyword' in request.GET:
          keyword = request.GET['keyword']

    if keyword:
               jobs = Job.objects.order_by('-created_at').filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
               jobs_count = jobs.count()
    context = {
          "jobs": jobs,
          "jobs_count": jobs_count,
          "keyword": keyword,
     }
    return render(request, "main/all-jobs.html",context)


@login_required(login_url = 'login')
def jobDetail(request,slug,pk):
     job = Job.objects.get(id=pk)
     context = {
          "job":job
     }
     return render(request,'main/job-detail.html',context)


@login_required(login_url = 'login')
def myCreatedJobs(request):
     jobs = Job.objects.filter(user__id=request.user.userprofile.id).order_by('-id')
     totalApplicant = Application()
     context = {
          'jobs':jobs
     }
     return render(request,'main/my-created-jobs.html',context)
     

# add job
@login_required(login_url = 'login')
def createJob(request):
     if request.user.userprofile.role != "employer":
               messages.warning(request, 'You are not allowed.')
               return redirect('myCreatedJobs')
     if request.method == "POST":
               
          form = jobForms(request.POST,request.FILES) 
          try:
               if form.is_valid():
                    form = form.save(commit=False)
                    form.user = request.user.userprofile
                    form.save()
                    messages.success(request, 'Your job has been created successfully.')
                    return redirect('myCreatedJobs')
          except:
                    messages.warning(request, 'Your job has been not created.')
                    return redirect('dashboard')
     else:
          form = jobForms()
          
     context = {
          'form':form
     }
     return render(request,'main/create-job.html',context)
          
@login_required(login_url = 'login')
def updateJob(request,pk):
     if request.user.userprofile.role != "employer":
               messages.warning(request, 'You are not allowed.')
               return redirect('myCreatedJobs')
     job = Job.objects.get(id = pk)
     if request.method == "POST":
               
          form = jobForms(request.POST,request.FILES ,instance = job ) 
          try:
               if form.is_valid():
                    form = form.save(commit=False)
                    form.save()
                    messages.success(request, 'Your job has been updated successfully.')
                    return redirect('myCreatedJobs')
          except:
                    messages.warning(request, 'Your job has been not updated.')
                    return redirect('dashboard')
     else:
          form = jobForms(instance = job)
          
     context = {
          'form':form
     }
     return render(request,'main/create-job.html',context)
          
          
@login_required(login_url = 'login')
def deleteJob(request,pk):
     job = Job.objects.get(id=pk)
     if request.user.userprofile == job.user:
          if request.method == "POST":
               job.delete()
               messages.success(request, 'Your job is deleted.')
               return redirect('myCreatedJobs')
     else:
          messages.warning(request, 'You are not allowed to delete the job.')
          return redirect('dashboard')
          
     context = {
          'job':job
     } 
     return render(request,'main/delete-job-confirmation.html',context)
     
     
# application job
@login_required(login_url = 'login')
def createApplication(request,pk):
     job = Job.objects.get(id=pk)
     if request.user.userprofile.role == "jobseeker":
          if request.method == "POST":
               form  = applicationForm(request.POST,request.FILES)
               try:
                    
                    if form.is_valid():
                         form = form.save(commit=False)
                         form.job = job
                         form.user = request.user.userprofile
                         form.save()
                         create_notification(request, job.user, 'application', extra_id=form.id)
                         messages.success(request, 'Your Applications is completed.')
                         return redirect('dashboard')
               except:
                    messages.success(request, 'Your Applications is not completed.Please try again')
                    return redirect('dashboard')
          else:
                    form  = applicationForm()
     else:
          messages.success(request, 'You are not allowed to apply for jobs')
          return redirect('dashboard')
     context = {
          'form':form
     }
     return render(request,'main/create-application-job.html',context)


@login_required(login_url = 'login')
def allApplication(request):
     applications = Application.objects.filter(user = request.user.userprofile)
     
     context = {
          'applications':applications
     }
     return render(request,'main/all-application-jobs.html',context)

     
@login_required(login_url = 'login')
def viewApplication(request,pk):
     
     if request.user.userprofile.role == "employer":
          application = get_object_or_404(Application,job__user = request.user.userprofile , id=pk)
     else:
          application = get_object_or_404(Application,user = request.user.userprofile , id=pk)
     # messages = ConversationMessages.objects.all()
     # serializer = ChatMessageSerializer(messages, many=True)
     # return Response(serializer.data)     
     if request.method == "POST":
          form = ConversationMessagesForm(request.POST or None)
          if form.is_valid():
               form = form.save(commit=False)
               form.created_by = request.user.userprofile
               form.application = application
               form.save()
               # print(application.user)
               if request.user.userprofile.role == "employer":
                    create_notification(request, application.user, 'message', extra_id=application.id)
               else:
                    create_notification(request, application.job.user, 'message', extra_id=application.id)
               # create_notification(request, application.created_by, 'message', extra_id=application.id)
               # messages.success(request, 'Your Applications is not completed.Please try again')
               return redirect('viewApplication',pk)
     else:
          form = ConversationMessagesForm()
     
     context = {
          'application':application,
          'form':form,
     }
     return render(request,'main/view-application-job.html',context)


@login_required(login_url = 'login')
def deleteApplication(request,pk):
     application = get_object_or_404(Application,user = request.user.userprofile , id=pk)
     
     if request.user.userprofile == application.user:
          if request.method == "POST":
               application.delete()
               messages.success(request, 'Your Application is deleted.')
               return redirect('allApplication')
     else:
          messages.warning(request, 'You are not allowed to delete the Application.')
          return redirect('dashboard')
          
     context = {
          'application':application
     } 
     return render(request,'main/delete-application-confirmation.html',context)


@login_required(login_url = 'login') 
def allApplicant(request,pk):
     job = get_object_or_404(Job,id = pk,user = request.user.userprofile)
     
     context = {
          'job':job
     }
     return render(request,'main/all-applicant.html',context)
     


#Notification
@login_required(login_url = 'login')
def notifications(request):
    goto = request.GET.get('goto', '')
    notification_id = request.GET.get('notification', 0)
    extra_id = request.GET.get('extra_id', 0)
    
    if goto != '':
        notification = Notification.objects.get(id=notification_id)
        notification.is_seen = True
        notification.save()
        if notification.notification_type == 'message':
            return redirect('viewApplication', notification.extra_id)
        elif notification.notification_type == 'application':
            return redirect('viewApplication', notification.extra_id)

    return render(request, 'main/notifications.html')


def sendMessages(request, pk):
    print("scfds")
    return JsonResponse('it is working', safe=False)


class ChatMessageAPIView(APIView):
    def get(self, request, application_id):
        messages = ConversationMessages.objects.filter(application__id = application_id )
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, application_id):
        serializer = ChatMessageSerializer(data=request.data,application__id = application_id)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
   

class apiConversion(viewsets.ModelViewSet):
    queryset = ConversationMessages.objects.all().order_by('-id')
    serializer_class = ChatMessageSerializer


def contactUs(request):
     if request.method=="POST":
          name = request.POST['name']
          email = request.POST['email']
          message = request.POST['message']
          contact_us = Contact.objects.create(name=name,email=email,message=message)
          contact_us.save()
          return redirect('home')
          
           
     return render(request,'main/contact-us.html')
     
#Riview
def Review_website(request):
     try:
         data = Review.objects.get(user=request.user.userprofile)
     except:
          data = ''
     if request.method == "POST":
          if data:
               description = request.POST['description']
               Review.objects.update(description= description)
               
          else:
               description = request.POST['description']
               data = Review.objects.create(description = description,user= request.user.userprofile)
          return redirect('Review_website')
     context = {
          'data':data
     }
     return render(request,'main/review.html',context)