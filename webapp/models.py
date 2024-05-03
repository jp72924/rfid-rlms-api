from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class CustomGroup(Group):
  authority = models.IntegerField(blank=True, null=True)


class Device(models.Model):
  id = models.AutoField(primary_key=True)
  chip_id = models.CharField(max_length=255, unique=True)


class Lock(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=255, unique=True)
  device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)
  min_auth = models.IntegerField(blank=True, null=True)


class Card(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.CharField(max_length=255, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  due_date = models.DateTimeField(blank=True, null=True)
  lock = models.ForeignKey(Lock, on_delete=models.CASCADE, null=True)
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  
  def is_overdue(self):
    """
    Checks if the current datetime is past the due_date of the model instance.
    """
    return timezone.now() > self.due_date # datetime.now().astimezone(self.due_date.tzinfo) > self.due_date


class AccessRecord(models.Model):

  timestamp = models.DateTimeField(auto_now_add=True)
  is_locked = models.BooleanField(default=False)
  card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True)
  lock = models.ForeignKey(Lock, on_delete=models.CASCADE, null=True)

  class Meta:
    ordering = ['-timestamp']  # Order logs by most recent first

  def __str__(self):
    return f"{self.timestamp} - "  # Truncate message for display


class ActivityRecord(models.Model):
  
  class Type(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'

  timestamp = models.DateTimeField(auto_now_add=True)
  type = models.CharField(max_length=6, choices=Type.choices)
  message = models.TextField()
  
  # Optional fields
  user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
  # Additional data fields can be added based on your needs

  class Meta:
    ordering = ['-timestamp']  # Order logs by most recent first

  def __str__(self):
    return f"{self.timestamp} - {self.type}: {self.message[:50]}"  # Truncate message for display