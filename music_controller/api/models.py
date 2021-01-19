from django.db import models
import random
import string
import django.utils.timezone

def generate_unique_code():
    length = 6
    
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=length))
        
        if Room.objects.filter(code=code).count() == 0:
            break
        
    return code


# Create your models here.

class Room(models.Model):
    code = models.CharField(max_length=8, default=generate_unique_code, unique=True)
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update_at = models.DateTimeField(auto_now=True)
    
class Message(models.Model):
    content = models.CharField(max_length=100, null=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=8, null=False)
    sent_by = models.CharField(max_length=50, null=False)