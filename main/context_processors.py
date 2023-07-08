from .models import Notification,Category
from accounts.models import UserProfile
def notifications(request):
          if request.user.is_authenticated:
              if UserProfile.objects.filter(user=request.user).exists() == True:
                    return {'notifications':request.user.userprofile.notifications.all()[:30],'notifications_count':request.user.userprofile.notifications.filter(is_seen=False)}
              else:
                    return {'notifications': []}

          else:
               return {'notifications':[]}
          
def categories(request):
     return {'categories':Category.objects.all()}