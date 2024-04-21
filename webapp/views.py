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
  
  
def authorize(request):
  """
  This function checks user access based on card UID, device ID, and lock status.

  Args:
      request: A Django HttpRequest object containing query parameters.

  Returns:
      A Django JsonResponse object with the authorization status.
  """

  # Extract data from request parameters
  card_uuid = request.GET.get('uuid')
  device_id = request.GET.get('dev')
  lock_status = int(request.GET.get('status', 0))  # Default lock status to 0

  # Try to retrieve card object
  try:
    card = Card.objects.get(uuid=card_uuid)
  except Card.DoesNotExist:
    return JsonResponse({"status": 0})  # Not authorized (card not found)

  # Check authorization conditions
  authorized = check_authorization(card, device_id, lock_status)

  # Prepare response based on authorization status
  response_message = {
      1: "AUTHORIZED",
      2: "DO NOT DISTURB",
      0: "NOT AUTHORIZED"
  }[authorized]

  return JsonResponse({"status": authorized, "message": response_message})

# Helper function to check authorization logic
def check_authorization(card, device_id, lock_status):
  return int(
      device_id == card.lock.device.chip_id and
      not card.is_overdue() and
      card.user.group.authority >= card.lock.min_auth) + int(lock_status and card.user.group.authority < 3)


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


def card_detail(request, uuid):
  view = 'cards'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  users = User.objects.all()
  try:
    card = Card.objects.get(uuid=uuid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  context = {'view': view, 'cards': cards, 'locks': locks, 'users': users, 'query': card}
  return render(request, 'webapp/cards.html', context)


def card_create(request):  
  if request.method == 'POST':
    card_uuid = request.POST.get('uuid')
    card_lock = Lock.objects.get(name=request.POST.get('lock'))
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    card_user = User.objects.get(username=request.POST.get('user'))

    card = Card(uuid=card_uuid, lock=card_lock, due_date=card_due_date, user=card_user)
    card.save()
  return redirect('card_list')


def card_update(request, uuid):
  try:
    card = Card.objects.get(uuid=uuid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  if request.method == 'POST':
    card_uuid = request.POST.get('uuid')
    card_lock = Lock.objects.get(name=request.POST.get('lock'))
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    card_user = User.objects.get(username=request.POST.get('user'))

    card.uuid = card_uuid
    card.lock = card_lock
    card.due_date = card_due_date
    card.user = card_user
    card.save()
    return redirect('card_detail', uuid=card.uuid)
  return redirect('card_list')


def card_delete(request, uuid):
  try:
    card = Card.objects.get(uuid=uuid)
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
    device = Device.objects.get(chip_id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  context = {'view': view, 'devices': devices, 'query': device}
  return render(request, 'webapp/devices.html', context)


def device_create(request):
  if request.method == 'POST':
    device_chip = request.POST.get('id')

    device = Device(chip_id=device_chip)
    device.save()
  return redirect('device_list')


def device_update(request, id):
  try:
    device = Device.objects.get(chip_id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  if request.method == 'POST':
    device_chip = request.POST.get('id')

    device.chip_id = device_chip
    device.save()
    return redirect('device_detail', id=device.chip_id)
  return redirect('device_list')


def device_delete(request, id):
  try:
    device = Device.objects.get(chip_id=id)
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


def group_detail(request, name):
  view = 'groups'
  groups = Group.objects.all()
  try:
    group = Group.objects.get(name=name)
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


def group_update(request, name):
  try:
    group = Group.objects.get(name=name)
  except Group.DoesNotExist:
    raise Http404("Group Not Found")
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_authority = request.POST.get('authority')

    group.name = group_name
    group.authority = group_authority
    group.save()
    return redirect('group_detail', name=group.name)
  return redirect('group_list')


def group_delete(request, name):
  try:
    group = Group.objects.get(name=name)
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


def lock_detail(request, name):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  try:
    lock = Lock.objects.get(name=name)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  context = {'view': view, 'locks': locks, 'devices': devices, 'query': lock}
  return render(request, 'webapp/locks.html', context)


def lock_create(request):  
  if request.method == 'POST':
    lock_name = request.POST.get('name')
    lock_device = Device.objects.get(chip_id=request.POST.get('device'))
    lock_auth = request.POST.get('auth')
    
    lock = Lock(name=lock_name, device=lock_device, min_auth=lock_auth)
    lock.save()
  return redirect('lock_list')


def lock_update(request, name):
  try:
    lock = Lock.objects.get(name=name)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  if request.method == 'POST':
    lock_name = request.POST.get('name')
    lock_device = Device.objects.get(chip_id=request.POST.get('device'))
    lock_auth = request.POST.get('auth')

    lock.name = lock_name
    lock.device = lock_device
    lock.min_auth = lock_auth
    lock.save()
    return redirect('lock_detail', name=lock.name)
  return redirect('lock_list')


def lock_delete(request, name):
  try:
    lock = Lock.objects.get(name=name)
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


def user_detail(request, username):
  view = 'users'
  users = User.objects.all()
  groups = Group.objects.all()
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  context = {'view': view, 'users': users, 'groups': groups, 'query': user}
  return render(request, 'webapp/users.html', context)


def user_create(request):  
  if request.method == 'POST':
    user_name = request.POST.get('username')
    user_group = Group.objects.get(name=request.POST.get('group'))
    
    user = User(username=user_name, group=user_group)
    user.save()
  return redirect('user_list')


def user_update(request, username):
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  if request.method == 'POST':
    user_name = request.POST.get('username')
    user_group = Group.objects.get(name=request.POST.get('group'))

    user.username = user_name
    user.group = user_group
    user.save()
    return redirect('user_detail', username=user.username)
  return redirect('user_list')


def user_delete(request, username):
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  user.delete()
  return redirect('user_list')