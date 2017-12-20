# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_extensions.db.fields import RandomCharField
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
#from django.contrib.auth.models import User
from push_notifications.models import APNSDevice, GCMDevice
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    apns_token = models.CharField(max_length=200)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        
# Create your models here.
class Submission(models.Model):
    id = RandomCharField(length=16, primary_key=True)
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1,
                              choices=[("s", "submitted"),("d", "done"),("p", "processing"),("e", "error"),('r', "removed")],
                              default='s')
    model = models.CharField(max_length=128,
                              choices=[('knee','knee'),('gait','gait')],
                              default='knee')
    video = models.FileField(upload_to='videos')
    processed_video = models.FileField(upload_to='processed', null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(auto_now=True, null=True)
    analysis = models.TextField(null=True)
    version = models.CharField(max_length=10, default='0.1a')

    def get_absolute_url(self):
        return reverse("analysis",kwargs={"sid":self.id})

@receiver(post_save, sender=Submission, dispatch_uid="send_notifications")
def send_notifications(sender, instance, **kwargs):
    if instance.status == "d":
        devices = APNSDevice.objects.filter(user=instance.user)
        devices.send_message(message={"title" : "Analysis", "body" : "You can view statistics of your swing now."}, extra={"video_id": instance.id})
#        devices.send_message("You can view statistics of your swing now.")

