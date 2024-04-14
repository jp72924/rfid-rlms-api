from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from webapp.models import Card
from webapp.models import Device
from webapp.models import Lock


def index(request):
  return HttpResponse("Hello, world. You're at the polls index.")
  
  
def auth(request):
  card_uid = request.GET.get('uid')
  device_id = request.GET.get('dev')
  
  authorized = 0
  
  try:
    card = Card.objects.get(uid=card_uid)
    authorized = int(device_id == card.lock.device.id) # type: ignore
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
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  context = {'view': view, 'cards': cards, 'locks': locks, 'query': card}
  return render(request, 'webapp/card_list.html', context)


def card_create(request):
  view = 'cards'
  cards = Card.objects.all()
  locks = Lock.objects.all()
  
  if request.method == 'POST':
    card_uid = request.POST.get('uid')
    card_lock = Lock(id=request.POST.get('lock'))
    print(card_uid, card_lock)
    if card_uid:
      card = Card(uid=card_uid, lock=card_lock)
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
  context = {'card': card}
  return render(request, 'webapp/card_update.html', context)


def card_delete(request, uid):
  try:
    card = Card.objects.get(uid=uid)
  except Card.DoesNotExist:
    raise Http404("Card Not Found")
  card.delete()
  return redirect('card_list')

# Devices

def device_list(request):
  devices = Device.objects.all()
  context = {'devices': devices}
  return render(request, 'webapp/device_list.html', context)


def device_detail(request, id):
  try:
    device = Device.objects.get(id=id)
  except Device.DoesNotExist:
    raise Http404("Card Not Found")
  context = {'device': device}
  return render(request, 'webapp/device_detail.html', context)


def device_create(request):
  if request.method == 'POST':
    device_id = request.POST.get('id')
    if device_id:
      device = Device(id=device_id)
      device.save()
      return redirect('device_list')
  context = {}
  return render(request, 'webapp/device_create.html', context)


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
  context = {'device': device}
  return render(request, 'webapp/device_update.html', context)


def device_delete(request, id):
  try:
    device = Device.objects.get(id=id)
  except Device.DoesNotExist:
    raise Http404("Device Not Found")
  device.delete()
  return redirect('device_list')

# Locks

def lock_list(request):
  locks = Lock.objects.all()
  context = {'locks': locks}
  return render(request, 'webapp/lock_list.html', context)


def lock_detail(request, id):
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  context = {'lock': lock}
  return render(request, 'webapp/lock_detail.html', context)


def lock_create(request):
  devices = Device.objects.all()
  
  if request.method == 'POST':
    lock_id = request.POST.get('id')
    lock_device = Device(id= request.POST.get('device_id'))
    if lock_id:
      lock = Lock(id=lock_id, device=lock_device)
      lock.save()
      return redirect('lock_list')
  context = {'devices': devices}
  return render(request, 'webapp/lock_create.html', context)


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
  context = {'lock': lock}
  return render(request, 'webapp/lock_update.html', context)


def lock_delete(request, id):
  try:
    lock = Lock.objects.get(id=id)
  except Lock.DoesNotExist:
    raise Http404("Lock Not Found")
  lock.delete()
  return redirect('lock_list')