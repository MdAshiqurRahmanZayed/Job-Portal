from .models import Notification

def notifications(request):
          if request.user.is_authenticated:
               return {'notifications':request.user.userprofile.notifications.all,'notifications_count':request.user.userprofile.notifications.filter(is_seen=False)}
          else:
               return {'notifications':[]}