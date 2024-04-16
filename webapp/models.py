from django.db import models
from django.utils import timezone

from datetime import datetime
import pytz


class Device(models.Model):
  id = models.CharField(max_length=255, primary_key=True)


class Lock(models.Model):
  id = models.IntegerField(primary_key=True)
  device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)


class Card(models.Model):
  uid = models.CharField(max_length=255, primary_key=True)
  created_at = models.DateTimeField(default=timezone.now)
  due_date = models.DateTimeField(blank=True, null=True)
  lock = models.ForeignKey(Lock, on_delete=models.CASCADE, null=True)
  # user = models.ForeignKey('User', on_delete=models.CASCADE)
  
  def is_overdue(self):
    """
    Checks if the current datetime is past the due_date of the model instance.
    """
    return datetime.now().astimezone(self.due_date.tzinfo) > self.due_date


class User(models.Model):
  id = models.CharField(max_length=255, primary_key=True)
  username = models.CharField(max_length=255)
  role = models.ForeignKey('Role', on_delete=models.CASCADE)


class Role(models.Model):
  id = models.IntegerField(primary_key=True)
  name = models.CharField(max_length=255)


class Record(models.Model):
  timestamp = models.DateTimeField(default=timezone.now)
  level = models.CharField(max_length=50, choices=[
      ('debug', 'Debug'),
      ('info', 'Info'),
      ('warning', 'Warning'),
      ('error', 'Error'),
      ('critical', 'Critical'),
  ])
  message = models.TextField()
  
  # Optional fields
  # user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
  # app_name = models.CharField(max_length=255, blank=True)
  # Additional data fields can be added based on your needs

  class Meta:
    ordering = ['-timestamp']  # Order logs by most recent first

  def __str__(self):
    return f"{self.timestamp} - {self.level}: {self.message[:50]}"  # Truncate message for display