from django.db import models
from django.utils import timezone


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
  user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
  
  def is_overdue(self):
    """
    Checks if the current datetime is past the due_date of the model instance.
    """
    return timezone.now() > self.due_date # datetime.now().astimezone(self.due_date.tzinfo) > self.due_date


class User(models.Model):
  id = models.AutoField(primary_key=True)
  username = models.CharField(max_length=255, unique=True)
  group = models.ForeignKey('Group', on_delete=models.CASCADE)


class Group(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=255, unique=True)
  authority = models.IntegerField(blank=True, null=True)


class Record(models.Model):
  timestamp = models.DateTimeField(auto_now_add=True)
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