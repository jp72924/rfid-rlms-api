from django.db import models
from django.utils import timezone


class Device(models.Model):
  id = models.CharField(max_length=255, primary_key=True)


class Lock(models.Model):
  id = models.IntegerField(primary_key=True)
  device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)


class Card(models.Model):
  uid = models.CharField(max_length=255, primary_key=True)
  created_at = models.DateTimeField(default=timezone.now)
  # due_date = models.DateTimeField(blank=True, null=True)
  lock = models.ForeignKey(Lock, on_delete=models.CASCADE, null=True)
  # user = models.ForeignKey('User', on_delete=models.CASCADE)


class User(models.Model):
  id = models.CharField(max_length=255, primary_key=True)
  username = models.CharField(max_length=255)
  role = models.ForeignKey('Role', on_delete=models.CASCADE)


class Role(models.Model):
  id = models.IntegerField(primary_key=True)
  name = models.CharField(max_length=255)
