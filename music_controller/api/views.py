from datetime import datetime
from django.http.response import JsonResponse
from rest_framework import generics, serializers, status
from django.shortcuts import render
from rest_framework.request import Request
from .models import Message, Room
from .serializers import CreateMessageSerializer, MessageSerializer, RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class RoomView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer
    
    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            host = self.request.session.session_key
            
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                self.request.session["room_code"] = room.code
                
                room.save(update_fields=["guest_can_pause", "votes_to_skip", "last_update_at"])
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                self.request.session["room_code"] = room.code
                
                room.save()
                
            return Response(data=RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        else:
            pass
        
class GetRoom(APIView):
    serializers_class = RoomSerializer
    lookup_url_kwarg = "code"
    
    def get(self, request, format=None):
        code = self.request.GET.get(self.lookup_url_kwarg)
        
        if code is not None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data["is_host"] = self.request.session.session_key == room[0].host
                
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"Room Not Found": "Invalid Room Code."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Bad Request": "Code arg not found in request."}, status=status.HTTP_400_BAD_REQUEST)
        
class JoinRoom(APIView):
    lookup_url_kwargs = "code"
    
    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        code = request.data.get(self.lookup_url_kwargs)
        
        if code is not None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session["room_code"] = code
                
                return Response({"Message": f"Room {code} Joined"}, status=status.HTTP_200_OK)
            
            else:
                return Response({"Message": f"Room {code} not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Bad Request": "Code arg not found in url"}, status=status.HTTP_400_BAD_REQUEST)
        
class UserInRoom(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        data = {
            "code": self.request.session.get("room_code")
        }
        
        return JsonResponse(data, status=status.HTTP_200_OK)
    
class LeaveRoom(APIView):
    def post(self, request, format=None):
        if "room_code" in self.request.session:
            self.request.session.pop("room_code")
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()
                
        return Response({"Message": "Success"}, status=status.HTTP_200_OK)
    
class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer
    
    def patch(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            code = serializer.data.get("code")
            
            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({"Message": f"Room {code} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            
            room = queryset[0]
            
            #? checking if user updating room is the host
            user_id = self.request.session.session_key
            if not room.host == user_id:
                return Response({"Message": f"You are not the host of room {code}"}, status=status.HTTP_403_FORBIDDEN)
            
            #? update room
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=["guest_can_pause", "votes_to_skip"])
            
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK) 
            
        else:
            return Response({"Bad Request": "Bad data"}, status=status.HTTP_400_BAD_REQUEST)
        
class SendMessage(APIView):
    serializer_class = CreateMessageSerializer
    
    def post(self, request, formats=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            message_content = serializer.data.get("content")
            room_code = self.request.session.get("room_code")
            
            if room_code is None:
                return Response({"message": "User not in a room"}, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = Room.objects.filter(code=room_code)
            if not queryset.exists():
                return Response({"Message": f"Room {room_code} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            
            if len(message_content) > 100:
                return Response({"Request too large": "Message too big, only messages of length < 100 are accepted"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            
            message = Message(sent_by=self.request.session.session_key, content=message_content, room=room_code)
            message.save()
            
            return Response({"message": "Message Created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Bad Request": "Bad data"}, status=status.HTTP_400_BAD_REQUEST)
        
class GetMessages(APIView):
    serializer_class = MessageSerializer
    
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        room_code = self.request.session.get("room_code", default=None)
        
        if room_code is None:
            return Response({"message": "User not in room"}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = list(Message.objects.all().filter(room=room_code))
        data = map(lambda message: self.serializer_class(message).data, queryset)
        
        return Response({"data": data}, status=status.HTTP_200_OK)
    