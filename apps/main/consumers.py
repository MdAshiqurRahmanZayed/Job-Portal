import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from apps.accounts.models import UserProfile

from .models import Application


class RealtimeConsumer(WebsocketConsumer):
    """Push-only: notifications and chat messages are created via the
    existing HTTP views and apps.main.services, never over this socket.

    One connection per page, not one per feature: every connection
    joins the user's own notifications group, and additionally joins a
    chat group when opened with an application_id (i.e. from the
    application's chat view). This avoids opening two separate
    sockets (one for the navbar's notification count, one for chat)
    on the same page.
    """

    def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            self.close()
            return

        profile = UserProfile.objects.filter(user=user).first()
        if profile is None:
            self.close()
            return

        self.group_names = [f"notifications_{profile.id}"]

        application_id = self.scope["url_route"]["kwargs"].get("application_id")
        if application_id is not None:
            # Mirrors viewApplication's permission check exactly: an
            # employer may join their own job's application chat, a
            # jobseeker may join their own submitted application's chat.
            if profile.role == "employer":
                application = Application.objects.filter(
                    job__user=profile, id=application_id
                ).first()
            else:
                application = Application.objects.filter(
                    user=profile, id=application_id
                ).first()

            if application is None:
                self.close()
                return

            self.group_names.append(f"chat_{application_id}")

        for group_name in self.group_names:
            async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        for group_name in getattr(self, "group_names", []):
            async_to_sync(self.channel_layer.group_discard)(
                group_name, self.channel_name
            )

    def receive(self, text_data=None, bytes_data=None):
        # Push-only consumer: client-sent data is intentionally ignored.
        # All notification/message creation goes through apps.main.services.
        pass

    def notification_new(self, event):
        self.send(text_data=json.dumps({"kind": "notification", **event["payload"]}))

    def chat_message(self, event):
        self.send(text_data=json.dumps({"kind": "chat", **event["payload"]}))
