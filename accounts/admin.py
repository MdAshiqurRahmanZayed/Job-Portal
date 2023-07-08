from django.contrib import admin
from .models import Account,UserProfile,Education
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class AccountAdmin(UserAdmin):
     list_display =('email','username','last_login','date_joined','is_active')
     
     list_display_links =('email',)
     readonly_fields = ('last_login','date_joined')
     ordering = ('-date_joined',)
      
     filter_horizontal =()
     list_filter = ()
     fieldsets = ()

     


admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile)
admin.site.register(Education)
