from rest_framework import serializers
from .models import Message, Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "code", "host", "guest_can_pause", "votes_to_skip", "created_at", "last_update_at") 
        
class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("guest_can_pause", "votes_to_skip")
        
class UpdateRoomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(validators=[])
    
    class Meta:
        model = Room
        fields = ("guest_can_pause", "votes_to_skip", "code")

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("content", "room", "sent_by", "sent_at")
        
class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("content",)