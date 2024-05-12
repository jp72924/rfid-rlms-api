from fileinput import filename
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from webapp.models import AccessRecord
from webapp.models import ActivityRecord
from webapp.models import Card
from webapp.models import LockGroup
from webapp.models import UserGroup
from webapp.models import Device
from webapp.models import Lock
from weasyprint import HTML

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


def log(request, type, message):
  activity_record = ActivityRecord(type=type, message=message, user=request.user)
  activity_record.save()


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
  is_locked = int(request.GET.get('status', 0))  # Default lock status to 0

  # Try to retrieve card object
  try:
    card = Card.objects.get(uuid=card_uuid)
  except Card.DoesNotExist:
    return JsonResponse({"status": 0})  # Not authorized (card not found)

  # Check authorization conditions
  authorized = has_authorization(card, device_id, is_locked)

  # Prepare response based on authorization status
  response_message = {
      1: "AUTHORIZED",
      2: "DO NOT DISTURB",
      0: "NOT AUTHORIZED"
  }[authorized]
  
  lock = Lock.objects.filter(device__chip_id=device_id).first()
  access_record = AccessRecord(is_locked=bool(is_locked), card=card, lock=lock)
  access_record.save()
  return JsonResponse({"status": authorized, "message": response_message})


def has_authorization(access_card, device_id, is_locked):
  """
  Checks if the user associated with the access card is authorized to access the lock.

  Args:
      access_card: The access card object used for access.
      device_id: The ID of the device containing the lock.
      is_locked: Whether the lock is currently locked.

  Returns:
      An integer representing the authorization level:
          0: Not authorized
          1: Authorized
          2: Not authorized with override (lock remains locked)
  """

  try:
    door_lock = Lock.objects.get(device__chip_id=device_id)
    lock_group = door_lock.groups.get()
    user_group = access_card.user.groups.get()
    authorized_group = UserGroup.objects.get(name=user_group.name)
    authorized = (lock_group in authorized_group.lock_groups.all() and not access_card.is_overdue())
  except (Lock.DoesNotExist, Group.DoesNotExist, UserGroup.DoesNotExist):
    return 0  # Missing association or object not found
  
  if authorized and (is_locked and not authorized_group.override_lock_pin):
    authorized = 2
  return authorized


def login_view(request):
  if not request.user.is_authenticated:
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user:
        login(request, user)
        
        title = f"Welcome, @{username}!"
        message = "You are successfully logged in"
        
        notify(request, "info", title, message)
        log(request, ActivityRecord.Type.LOGIN, message)
        return redirect('card_list')  # Redirect to your homepage
      else:
        # Login failed
        notify(request, "danger", 'Login failed', 'Username or password was incorrect')
  
    return render(request, 'webapp/login.html')
  return redirect('card_list')


@login_required
def logout_view(request):  
  # title = f"Goodbye, until next time!"
  message = "You are successfully logged out"
        
  # notify(request, "info", title, message)
  log(request, ActivityRecord.Type.LOGOUT, message)
  
  logout(request)
  # Optionally redirect to a specific page after logout
  return redirect('login')  # Replace 'login' with your login URL name


@login_required
def booking(request):
  view = 'booking'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  users = User.objects.all()
  context = {'view': view, 'cards': cards, 'locks': locks, 'users': users}
  return render(request, 'webapp/booking.html', context)


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
  users = User.objects.all()
  try:
    card = Card.objects.get(uuid=uuid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  context = {'view': view, 'cards': cards, 'users': users, 'query': card}
  return render(request, 'webapp/cards.html', context)


@login_required
def card_create(request):  
  if request.method == 'POST':
    card_uuid = request.POST.get('uuid')
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    card_user = User.objects.get(username=request.POST.get('user'))

    card = Card(uuid=card_uuid, due_date=card_due_date, user=card_user)
    card.save()

    title = f"New card added"
    message = f"Access granted to @{card_user.username}"
    
    notify(request, "success", title, message)
    log(request, ActivityRecord.Type.CREATE, message)
  return redirect('card_list')


@login_required
def card_update(request, uuid):
  try:
    card = Card.objects.get(uuid=uuid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  if request.method == 'POST':
    card_uuid = request.POST.get('uuid')
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    card_user = User.objects.get(username=request.POST.get('user'))

    card.uuid = card_uuid
    card.due_date = card_due_date
    card.user = card_user
    card.save()
    
    title = f"Card updated"
    message = f"@{card_user.username} now has access until {card_due_date}"
    
    notify(request, "info", title, message)
    log(request, ActivityRecord.Type.UPDATE, message)
    
    return redirect('card_detail', uuid=card.uuid)
  return redirect('card_list')


@login_required
def card_delete(request, uuid):
  try:
    card = Card.objects.get(uuid=uuid)
    card_user = card.user
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  card.delete()
  
  title = f"Card removed"
  message = f"Access revoked to @{card_user.username}"
  
  notify(request, "danger", title, message)
  log(request, ActivityRecord.Type.DELETE, message)
  
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
    
    title = f"New device added"
    message = f"{device_chip} is now available"
    
    notify(request, "success", title, message)
    log(request, ActivityRecord.Type.CREATE, message)
    
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
    
    title = f"Device updated"
    message = f"Record updated from {id} to {device_chip}"
    
    notify(request, "info", title, message)
    log(request, ActivityRecord.Type.UPDATE, message)
    
    return redirect('device_detail', id=device.chip_id)
  return redirect('device_list')


@login_required
def device_delete(request, id):
  try:
    device = Device.objects.get(chip_id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  device.delete()
  
  title = f"Device removed"
  message = f"{device.chip_id} is not longer available"
  
  notify(request, "danger", title, message)
  log(request, ActivityRecord.Type.DELETE, message)
  
  return redirect('device_list')

# Locks

@login_required
def lock_list(request):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  groups = LockGroup.objects.all()
  context = {'view': view, 'locks': locks, 'devices': devices, 'groups': groups}
  return render(request, 'webapp/locks.html', context)


@login_required
def lock_detail(request, name):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  groups = LockGroup.objects.all()
  try:
    lock = Lock.objects.get(name=name)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  context = {'view': view, 'locks': locks, 'devices': devices, 'groups': groups, 'query': lock}
  return render(request, 'webapp/locks.html', context)


@login_required
def lock_create(request):  
  if request.method == 'POST':
    lock_name = request.POST.get('name')
    lock_device = Device.objects.get(chip_id=request.POST.get('device'))
    lock_group = LockGroup.objects.get(name=request.POST.get('lock-group'))
    
    lock = Lock(name=lock_name, device=lock_device)
    lock.save()
    
    lock.groups.set([lock_group])
    
    title = f"New lock added"
    message = f"{lock_name} is linked to {lock_device.chip_id}"

    notify(request, "success", title, message)
    log(request, ActivityRecord.Type.CREATE, message)

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
    lock_group = LockGroup.objects.get(name=request.POST.get('lock-group'))

    lock.name = lock_name
    lock.device = lock_device
    lock.save()
    
    lock.groups.set([lock_group])
    
    title = f"Lock updated"
    message = f"{lock_name} is now linked to {lock_device.chip_id}"
    
    notify(request, "info", title, message)
    log(request, ActivityRecord.Type.UPDATE, message)
    
    return redirect('lock_detail', name=lock.name)
  return redirect('lock_list')


@login_required
def lock_delete(request, name):
  try:
    lock = Lock.objects.get(name=name)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  lock.delete()
  
  title = f"Lock removed"
  message = f"{lock.name} is no longer linked to {lock.device.chip_id}, it is no longer accessible"
  
  notify(request, "danger", title, message)
  log(request, ActivityRecord.Type.DELETE, message)
  
  return redirect('lock_list')

# Lock groups

@login_required
def group_lock_list(request):
  view = 'lock_groups'
  lock_groups = LockGroup.objects.all()
  context = {'view': view, 'lock_groups': lock_groups}
  return render(request, 'webapp/lock_groups.html', context)


@login_required
def group_lock_detail(request, name):
  view = 'lock_groups'
  lock_groups = LockGroup.objects.all()
  try:
    group = LockGroup.objects.get(name=name)
  except LockGroup.DoesNotExist:
    raise Http404("LockGroup Not Found")
  context = {'view': view, 'lock_groups': lock_groups, 'query': group}
  return render(request, 'webapp/lock_groups.html', context)


@login_required
def group_lock_create(request):  
  if request.method == 'POST':
    group_name = request.POST.get('name')

    group = LockGroup.objects.create(name=group_name)
    group.save()
  return redirect('group_lock_list')


@login_required
def group_lock_update(request, name):
  try:
    group = LockGroup.objects.get(name=name)
  except LockGroup.DoesNotExist:
    raise Http404("LockGroup Not Found")
  if request.method == 'POST':
    group_name = request.POST.get('name')

    group.name = group_name
    group.save()
  return redirect('group_lock_list')


@login_required
def group_lock_delete(request, name):
  try:
    group = LockGroup.objects.get(name=name)
  except LockGroup.DoesNotExist:
    raise Http404("LockGroup Not Found")
  group.delete()
  
  return redirect('group_lock_list')

# User groups

@login_required
def group_user_list(request):
  view = 'user_groups'
  user_groups = UserGroup.objects.all()
  lock_groups = LockGroup.objects.all()
  context = {'view': view, 'user_groups': user_groups, 'lock_groups': lock_groups}
  return render(request, 'webapp/user_groups.html', context)


@login_required
def group_user_detail(request, name):
  view = 'user_groups'
  user_groups = UserGroup.objects.all()
  lock_groups = LockGroup.objects.all()
  try:
    user_group = UserGroup.objects.get(name=name)
  except UserGroup.DoesNotExist:
    raise Http404("UserGroup Not Found")
  context = {'view': view, 'user_groups': user_groups, 'lock_groups': lock_groups, 'query': user_group}
  return render(request, 'webapp/user_groups.html', context)


@login_required
def group_user_create(request):  
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_master_access = request.POST.get('master-access') != None
    
    selected_lock_groups = [lock_group for lock_group in LockGroup.objects.all() if request.POST.get(lock_group.tag()) is not None]

    group = UserGroup.objects.create(name=group_name, override_lock_pin=group_master_access)
    group.lock_groups.set(selected_lock_groups)
    group.save()
    
  return redirect('group_user_list')


@login_required
def group_user_update(request, name):
  try:
    group = UserGroup.objects.get(name=name)
  except UserGroup.DoesNotExist:
    raise Http404("UserGroup Not Found")
  if request.method == 'POST':
    group_name = request.POST.get('name')
    group_master_access = request.POST.get('master-access') != None
    
    selected_lock_groups = [lock_group for lock_group in LockGroup.objects.all() if request.POST.get(lock_group.tag()) is not None]

    group.name = group_name
    group.override_lock_pin = group_master_access
    group.lock_groups.set(selected_lock_groups)
    group.save()
    
  return redirect('group_user_list')


@login_required
def group_user_delete(request, name):
  try:
    group = UserGroup.objects.get(name=name)
  except UserGroup.DoesNotExist:
    raise Http404("UserGroup Not Found")
  group.delete()
  
  return redirect('group_user_list')

# Users

@login_required
def user_list(request):
  view = 'users'
  users = User.objects.all()
  groups = UserGroup.objects.all()
  context = {'view': view, 'users': users, 'groups': groups}
  return render(request, 'webapp/users.html', context)


@login_required
def user_detail(request, username):
  view = 'users'
  users = User.objects.all()
  groups = UserGroup.objects.all()
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  context = {'view': view, 'users': users, 'groups': groups, 'query': user}
  return render(request, 'webapp/users.html', context)


@login_required
def user_create(request):  
  if request.method == 'POST':
    user_first_name = request.POST.get('first-name')
    user_last_name = request.POST.get('last-name')
    user_name = request.POST.get('username')
    user_password = request.POST.get('password')
    user_email = request.POST.get('email')
    user_group = UserGroup.objects.get(name=request.POST.get('group'))
    
    user = User.objects.create_user(username=user_name, password=user_password, email=user_email, first_name=user_first_name, last_name=user_last_name)
    user.groups.set([user_group])
    
    title = f"New user added"
    message = f"@{user_name} added to {user_group.name} group"
    
    notify(request, "success", title, message)
    log(request, ActivityRecord.Type.CREATE, message)
    
  return redirect('user_list')


@login_required
def user_update(request, username):
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    raise Http404("User Not Found")
  if request.method == 'POST':
    user_first_name = request.POST.get('first-name')
    user_last_name = request.POST.get('last-name')
    user_name = request.POST.get('username')
    user_password = request.POST.get('password')
    user_email = request.POST.get('email')
    user_group = UserGroup.objects.get(name=request.POST.get('group'))

    user.username = user_name
    user.set_password(user_password)
    user.email = user_email
    user.first_name = user_first_name
    user.last_name = user_last_name
    user.save()
    
    user.groups.set([user_group])
    
    title = f"User updated"
    message = f"@{user_name} updated to {user_group.name} group"
    
    notify(request, "info", title, message)
    log(request, ActivityRecord.Type.UPDATE, message)
    
  return redirect('user_list')


@login_required
def user_delete(request, username):
  try:
    user = User.objects.get(username=username)
    user_group = user.groups.first()
  except User.DoesNotExist:
    raise Http404("User Not Found")
  user.delete()
  
  title = f"User removed"
  message = f"@{user.username} added to {user_group.name} group"
  
  notify(request, "danger", title, message)
  log(request, ActivityRecord.Type.DELETE, message)
  
  return redirect('user_list')


@login_required
def logs(request):
  view = 'logs'
  activity_records = ActivityRecord.objects.all()
  context = {'view': view, 'activity_records': activity_records}
  return render(request, 'webapp/logs.html', context)


@login_required
def report(request, name):
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d")
    
    doc_name = f"{name} Access Log"
    filename = f"{name.upper()}_{timestamp}.pdf"
  
    # Get data for the PDF (from model, queryset, etc.)
    access_records = AccessRecord.objects.filter(lock__name=name)
    context = {'access_records': access_records, 'doc_name': doc_name}
    
    # Render the HTML template with the data
    html_template = render(request, 'webapp/report.html', context)

    # Generate the PDF using Weasyprint
    pdf = HTML(string=html_template.content).write_pdf()

    # Set the response headers for PDF download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="{}"'.format(filename)

    return response