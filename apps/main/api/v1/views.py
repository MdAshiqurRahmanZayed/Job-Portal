from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.main.models import ConversationMessages, Notification

from .serializers import ChatMessageSerializer


class ChatMessageAPIView(APIView):
    def get(self, request, application_id):
        messages = ConversationMessages.objects.filter(application__id=application_id)
        serializer = ChatMessageSerializer(messages, many=True)
        related_notifications = Notification.objects.filter(
            to_user=request.user.userprofile, application__id=application_id
        )
        related_notifications.update(is_seen=True)
        return Response(serializer.data)

    def post(self, request, application_id):
        data = request.data.copy()
        data["application"] = application_id
        serializer = ChatMessageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class apiConversion(viewsets.ModelViewSet):
    queryset = ConversationMessages.objects.all().order_by("-id")
    serializer_class = ChatMessageSerializer
