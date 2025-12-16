from django.contrib import admin

from .models import (
    AboutPage,
    Application,
    Category,
    Contact,
    ConversationMessages,
    Job,
    Notification,
    Review,
    teamMember,
)


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}  # new
    list_display = ("name", "modified_at")


class jobAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}  # new
    list_display = ("title", "modified_at")


class applicationAdmin(admin.ModelAdmin):
    list_display = ("job", "user")


class ConversationMessagesAdmin(admin.ModelAdmin):
    list_display = ("application", "created_by")


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_by", "to_user", "is_seen")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Job, jobAdmin)
admin.site.register(Application, applicationAdmin)
admin.site.register(ConversationMessages, ConversationMessagesAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Contact)
admin.site.register(Review)
admin.site.register(AboutPage)
admin.site.register(teamMember)
