from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from webapp.models import CustomGroup
from webapp.models import Card
from webapp.models import Device
from webapp.models import Lock
from webapp.models import Record

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


def notify(request, type, title, content):
  message = {'type': type, 'title': title, 'content': content}
  request.session['message'] = message
  
  
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
  group = CustomGroup.objects.get(name=card.user.groups.first().name)
  return int(
      device_id == card.lock.device.chip_id and
      not card.is_overdue() and
      group.authority >= card.lock.min_auth) + int(lock_status and group.authority < 3)


def login_view(request):
  if not request.user.is_authenticated:
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user:
        login(request, user)
        notify(request, "info", f"Welcome, @{username}!", 'You are successfully logged in')
        return redirect('booking')  # Redirect to your homepage
      else:
        # Login failed
        notify(request, "info", 'Login Failed', 'Username or password was incorrect')
  
    return render(request, 'webapp/login.html')
  return redirect('booking')

@login_required
def logout_view(request):
  logout(request)
  # Optionally redirect to a specific page after logout
  return redirect('login')  # Replace 'login' with your login URL name


@login_required
def booking(request):
  view = 'booking'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  context = {'view': view, 'cards': cards, 'locks': locks}
  return render(request, 'webapp/booking.html', context)

# Cards

@login_required
def card_list(request):
  view = 'cards'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  users = User.objects.all()
  context = {'view': view, 'cards': cards, 'locks': locks, 'users': users}
  return render(request, 'webapp/cards.html', context)

@login_required
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


@login_required
def card_create(request):  
  if request.method == 'POST':
    card_uuid = request.POST.get('uuid')
    card_lock = Lock.objects.get(name=request.POST.get('lock'))
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    card_user = User.objects.get(username=request.POST.get('user'))

    card = Card(uuid=card_uuid, lock=card_lock, due_date=card_due_date, user=card_user)
    card.save()
    notify(request, "success", f"New card added", f"Access granted to @{card_user.username} for {card_lock.name}")
  return redirect('card_list')


@login_required
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
    notify(request, "info", f"Card updated", f"@{card_user.username} now has access to {card_lock.name} until {card_due_date}")
    return redirect('card_detail', uuid=card.uuid)
  return redirect('card_list')


@login_required
def card_delete(request, uuid):
  try:
    card = Card.objects.get(uuid=uuid)
    card_lock = card.lock
    card_user = card.user
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  card.delete()
  notify(request, "danger", f"Card removed", f"Access revoked to @{card_user.username} for {card_lock.name}")
  return redirect('card_list')

# Devices

@login_required
def device_list(request):
  view = 'devices'
  devices = Device.objects.all()
  context = {'view': view, 'devices': devices}
  return render(request, 'webapp/devices.html', context)


@login_required
def device_detail(request, id):
  view = 'devices'
  devices = Device.objects.all()
  try:
    device = Device.objects.get(chip_id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  context = {'view': view, 'devices': devices, 'query': device}
  return render(request, 'webapp/devices.html', context)


@login_required
def device_create(request):
  if request.method == 'POST':
    device_chip = request.POST.get('chip-id')

    device = Device(chip_id=device_chip)
    device.save()
    notify(request, "success", f"New device added", f"{device_chip} is now available")
  return redirect('device_list')


@login_required
def device_update(request, id):
  try:
    device = Device.objects.get(chip_id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  if request.method == 'POST':
    device_chip = request.POST.get('chip-id')

    device.chip_id = device_chip
    device.save()
    notify(request, "info", f"Device updated", f"Record updated from {id} to {device_chip}")
    return redirect('device_detail', id=device.chip_id)
  return redirect('device_list')


@login_required
def device_delete(request, id):
  try:
    device = Device.objects.get(chip_id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  device.delete()
  notify(request, "danger", f"Device removed", f"{device.chip_id} is not longer available")
  return redirect('device_list')

# Groups

@login_required
def group_list(request):
  view = 'groups'
  groups = CustomGroup.objects.all()
  context = {'view': view, 'groups': groups}
  return render(request, 'webapp/groups.html', context)


@login_required
def group_detail(request, name):
  view = 'groups'
  groups = CustomGroup.objects.all()
  try:
    group = CustomGroup.objects.get(name=name)
  except CustomGroup.DoesNotExist:
    raise Http404("CustomGroup Not Found")
  context = {'view': view, 'groups': groups, 'query': group}
  return render(request, 'webapp/groups.html', context)


@login_required
def group_create(request):  
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_authority = request.POST.get('authority')

    group = CustomGroup.objects.create(name=group_name)
    group.authority = group_authority
    group.save()
    notify(request, "success", f"New group added", f"{group_name} is now available")
  return redirect('group_list')


@login_required
def group_update(request, name):
  try:
    group = CustomGroup.objects.get(name=name)
  except CustomGroup.DoesNotExist:
    raise Http404("CustomGroup Not Found")
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_authority = request.POST.get('authority')

    group.name = group_name
    group.authority = group_authority
    group.save()
    notify(request, "info", f"Group updated", f"{group_name} now has access to authority {group_authority} features")
    return redirect('group_detail', name=group.name)
  return redirect('group_list')


@login_required
def group_delete(request, name):
  try:
    group = CustomGroup.objects.get(name=name)
  except CustomGroup.DoesNotExist:
    raise Http404("CustomGroup Not Found")
  group.delete()
  notify(request, "danger", f"Group removed", f"{name} is not longer available")
  return redirect('group_list')

# Locks

@login_required
def lock_list(request):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  context = {'view': view, 'locks': locks, 'devices': devices}
  return render(request, 'webapp/locks.html', context)


@login_required
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


@login_required
def lock_create(request):  
  if request.method == 'POST':
    lock_name = request.POST.get('name')
    lock_device = Device.objects.get(chip_id=request.POST.get('device'))
    lock_auth = request.POST.get('auth')
    
    lock = Lock(name=lock_name, device=lock_device, min_auth=lock_auth)
    lock.save()
    notify(request, "success", f"New lock added", f"{lock_name} is linked to {lock_device.chip_id}, authority {lock_auth} or higher is required for access")
  return redirect('lock_list')


@login_required
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
    notify(request, "info", f"Lock updated", f"{lock_name} is now linked to {lock_device.chip_id}, authority {lock_auth} or higher is required for access")
    return redirect('lock_detail', name=lock.name)
  return redirect('lock_list')


@login_required
def lock_delete(request, name):
  try:
    lock = Lock.objects.get(name=name)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  lock.delete()
  notify(request, "danger", f"Lock removed", f"{lock.name} is no longer linked to {lock.device.chip_id}, it is no longer accessible")
  return redirect('lock_list')

# Users

@login_required
def user_list(request):
  view = 'users'
  users = User.objects.all()
  groups = CustomGroup.objects.all()
  context = {'view': view, 'users': users, 'groups': groups}
  return render(request, 'webapp/users.html', context)


@login_required
def user_detail(request, username):
  view = 'users'
  users = User.objects.all()
  groups = CustomGroup.objects.all()
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  context = {'view': view, 'users': users, 'groups': groups, 'query': user}
  return render(request, 'webapp/users.html', context)


@login_required
def user_create(request):  
  if request.method == 'POST':
    user_name = request.POST.get('username')
    user_password = request.POST.get('password')
    user_email = request.POST.get('email')
    user_group = CustomGroup.objects.get(name=request.POST.get('group'))
    
    user = User.objects.create_user(username=user_name, password=user_password, email=user_email)
    user.groups.clear()
    user.groups.add(user_group)
    notify(request, "success", f"New user added", f"{user_name} added to {user_group.name} group")
  return redirect('user_list')


@login_required
def user_update(request, username):
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  if request.method == 'POST':
    user_name = request.POST.get('username')
    user_password = request.POST.get('password')
    user_email = request.POST.get('email')
    user_group = CustomGroup.objects.get(name=request.POST.get('group'))

    user.username = user_name
    user.set_password(user_password)
    user.email = user_email
    user.groups.clear()
    user.groups.add(user_group)
    user.save()
    notify(request, "info", f"User updated", f"{user_name} updated to {user_group.name} group")
    return redirect('user_detail', username=user.username)
  return redirect('user_list')


@login_required
def user_delete(request, username):
  try:
    user = User.objects.get(username=username)
    user_group = user.groups.first()
  except User.DoesNotExist:
    raise Http404("User Not Found")
  user.delete()
  notify(request, "danger", f"User removed", f"{user.username} added to {user_group.name} group")
  return redirect('user_list')


@login_required
def logs(request):
  view = 'logs'
  records = Record.objects.all()
  context = {'view': view, 'records': records}
  return render(request, 'webapp/logs.html', context)