from rest_framework import serializers
from .models import ConversationMessages


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessages
        fields = '__all__'
