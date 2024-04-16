from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from webapp.models import Card
from webapp.models import Device
from webapp.models import Lock

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
  
  authorized = 0
  
  try:
    card = Card.objects.get(uid=card_uid)
    authorized = int(device_id == card.lock.device.id and not card.is_overdue()) # type: ignore
  except Card.DoesNotExist:
    pass
  
  if authorized:
    print('AUTHORIZED')
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
  context = {'view': view, 'cards': cards, 'locks': locks}
  return render(request, 'webapp/card_list.html', context)


def card_detail(request, uid):
  view = 'cards'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  try:
    card = Card.objects.get(uid=uid)
    print(card.is_overdue())
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  context = {'view': view, 'cards': cards, 'locks': locks, 'query': card}
  return render(request, 'webapp/card_list.html', context)


def card_create(request):  
  if request.method == 'POST':
    card_uid = request.POST.get('uid')
    print(card_uid)
    card_lock = Lock(id=request.POST.get('lock'))
    card_due_date = convert_to_django_date(request.POST.get('due-date'))
    if card_uid:
      card = Card(uid=card_uid, lock=card_lock, due_date=card_due_date)
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
  return render(request, 'webapp/device_list.html', context)


def device_detail(request, id):
  view = 'devices'
  devices = Device.objects.all()
  try:
    device = Device.objects.get(id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  context = {'view': view, 'devices': devices, 'query': device}
  return render(request, 'webapp/device_list.html', context)


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

# Locks

def lock_list(request):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  context = {'view': view, 'locks': locks, 'devices': devices}
  return render(request, 'webapp/lock_list.html', context)


def lock_detail(request, id):
  view = 'locks'
  locks = Lock.objects.all()
  devices = Device.objects.all()
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  context = {'view': view, 'locks': locks, 'devices': devices, 'query': lock}
  return render(request, 'webapp/lock_list.html', context)


def lock_create(request):  
  if request.method == 'POST':
    lock_id = request.POST.get('id')
    lock_device = Device(id=request.POST.get('device'))
    if lock_id:
      lock = Lock(id=lock_id, device=lock_device)
      lock.save()
  return redirect('lock_list')


def lock_update(request, id):
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  if request.method == 'POST':
    lock_id = request.POST.get('id')
    if lock_id:
      lock.id = lock_id
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