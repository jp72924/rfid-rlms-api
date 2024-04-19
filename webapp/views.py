from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from webapp.models import Card
from webapp.models import Device
from webapp.models import Group
from webapp.models import Lock
from webapp.models import User

from datetime import datetime


def convert_to_django_date(datetime_str):
  """Converts a string in 'YYYY-MM-DDThh:mm' format to a Django model date.

  Args:
      datetime_str: The string representation of the datetime in ISO 8601 format.

  Returns:
      A Django model date object representing the parsed datetime.
  """
  try:
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
    return datetime_obj # Extract the date portion for Django model
  except ValueError:
    raise ValueError(f"Invalid datetime string format: {datetime_str}")


def index(request):
  return HttpResponse("Hello, world. You're at the polls index.")
  
  
def auth(request):
  card_uid = request.GET.get('uid')
  device_id = request.GET.get('dev')
  lock_status = int(request.GET.get('status'))
  
  authorized = 0
  
  try:
    card = Card.objects.get(uid=card_uid)
    authorized = int(device_id == card.lock.device.id and not card.is_overdue() and card.user.group.authority >= card.lock.min_auth) # type: ignore
    if lock_status and card.user.group.authority < 3:
       authorized = 2
  except Card.DoesNotExist:
    pass
  
  if authorized == 1:
    print('AUTHORIZED')
  elif authorized == 2:
    print('DO NOT DISTURB')
  else:
    print('NOT AUTHORIZED')
  
  data = {
    "status": authorized
  }
  
  return JsonResponse(data)


def booking(request):
  view = 'booking'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  context = {'view': view, 'cards': cards, 'locks': locks}
  return render(request, 'webapp/booking.html', context)

# Cards

def card_list(request):
  view = 'cards'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  users = User.objects.all()
  context = {'view': view, 'cards': cards, 'locks': locks, 'users': users}
  return render(request, 'webapp/cards.html', context)


def card_detail(request, uid):
  view = 'cards'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  users = User.objects.all()
  try:
    card = Card.objects.get(uid=uid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  context = {'view': view, 'cards': cards, 'locks': locks, 'users': users, 'query': card}
  return render(request, 'webapp/cards.html', context)


def card_create(request):  
  if request.method == 'POST':
    card_uid = request.POST.get('uid')
    card_lock = Lock(id=request.POST.get('lock'))
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    card_user = User(id=request.POST.get('user'))
    if card_uid:
      card = Card(uid=card_uid, lock=card_lock, due_date=card_due_date, user=card_user)
      card.save()
  return redirect('card_list')


def card_update(request, uid):
  try:
    card = Card.objects.get(uid=uid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  if request.method == 'POST':
    card_uid = request.POST.get('uid')
    if card_uid:
      card.uid = card_uid
      card.save()
      return redirect('card_detail', uid=card.uid)
  return redirect('card_list')


def card_delete(request, uid):
  try:
    card = Card.objects.get(uid=uid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  card.delete()
  return redirect('card_list')

# Devices

def device_list(request):
  view = 'devices'
  devices = Device.objects.all()
  context = {'view': view, 'devices': devices}
  return render(request, 'webapp/devices.html', context)


def device_detail(request, id):
  view = 'devices'
  devices = Device.objects.all()
  try:
    device = Device.objects.get(id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  context = {'view': view, 'devices': devices, 'query': device}
  return render(request, 'webapp/devices.html', context)


def device_create(request):
  if request.method == 'POST':
    device_id = request.POST.get('id')
    if device_id:
      device = Device(id=device_id)
      device.save()
  return redirect('device_list')


def device_update(request, id):
  try:
    device = Device.objects.get(id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  if request.method == 'POST':
    device_id = request.POST.get('id')
    if device_id:
      device.id = device_id
      device.save()
      return redirect('device_detail', id=device.id)
  return redirect('device_list')


def device_delete(request, id):
  try:
    device = Device.objects.get(id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  device.delete()
  return redirect('device_list')

# Groups

def group_list(request):
  view = 'groups'
  groups = Group.objects.all()
  context = {'view': view, 'groups': groups}
  return render(request, 'webapp/groups.html', context)


def group_detail(request, id):
  view = 'groups'
  groups = Group.objects.all()
  try:
    group = Group.objects.get(id=id)
  except Group.DoesNotExist:
    raise Http404("Group Not Found")
  context = {'view': view, 'groups': groups, 'query': group}
  return render(request, 'webapp/groups.html', context)


def group_create(request):  
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_authority = request.POST.get('authority')

    group = Group(name=group_name, authority=group_authority)
    group.save()
  return redirect('group_list')


def group_update(request, id):
  try:
    group = Group.objects.get(id=id)
  except Group.DoesNotExist:
    raise Http404("Group Not Found")
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_authority = request.POST.get('authority')

    group.name = group_name
    group.authority = group_authority
    group.save()
    return redirect('group_detail', id=group.id)
  return redirect('group_list')


def group_delete(request, id):
  try:
    group = Group.objects.get(id=id)
  except Group.DoesNotExist:
    raise Http404("Group Not Found")
  group.delete()
  return redirect('group_list')

# Locks

def lock_list(request):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  context = {'view': view, 'locks': locks, 'devices': devices}
  return render(request, 'webapp/locks.html', context)


def lock_detail(request, id):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  context = {'view': view, 'locks': locks, 'devices': devices, 'query': lock}
  return render(request, 'webapp/locks.html', context)


def lock_create(request):  
  if request.method == 'POST':
    lock_id = request.POST.get('id')
    lock_device = Device(id=request.POST.get('device'))
    lock_auth = request.POST.get('auth')
    if lock_id:
      lock = Lock(id=lock_id, device=lock_device, min_auth=lock_auth)
      lock.save()
  return redirect('lock_list')


def lock_update(request, id):
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  if request.method == 'POST':
    lock_id = request.POST.get('id')
    lock_auth = request.POST.get('auth')
    if lock_id:
      lock.id = lock_id
      lock.min_auth = lock_auth
      lock.save()
      return redirect('lock_detail', id=lock.id)
  return redirect('lock_list')


def lock_delete(request, id):
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  lock.delete()
  return redirect('lock_list')

# Users

def user_list(request):
  view = 'users'
  users = User.objects.all()
  groups = Group.objects.all()
  context = {'view': view, 'users': users, 'groups': groups}
  return render(request, 'webapp/users.html', context)


def user_detail(request, id):
  view = 'users'
  users = User.objects.all()
  groups = Group.objects.all()
  try:
    user = User.objects.get(id=id)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  context = {'view': view, 'users': users, 'groups': groups, 'query': user}
  return render(request, 'webapp/users.html', context)


def user_create(request):  
  if request.method == 'POST':
    user_id = request.POST.get('id')
    user_name = request.POST.get('username')
    user_group = Group(id=request.POST.get('group'))
    if user_id:
      user = User(id=user_id, username=user_name, group=user_group)
      user.save()
  return redirect('user_list')


def user_update(request, id):
  try:
    user = User.objects.get(id=id)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  if request.method == 'POST':
    user_id = request.POST.get('id')
    user_name = request.POST.get('name')
    if user_id:
      user.id = user_id
      user.username = user_name
      user.save()
      return redirect('user_detail', id=user.id)
  return redirect('user_list')


def user_delete(request, id):
  try:
    user = User.objects.get(id=id)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  user.delete()
  return redirect('user_list')