from django.urls import path

from webapp import views

urlpatterns = [
  path('auth', views.auth, name='auth'),
  
  path('card/list', views.card_list, name='card_list'),  # List all cards
  path('card/create', views.card_create, name='card_create'),  # Create a new card
  path('card/<str:uid>', views.card_detail, name='card_detail'),  # Detail view for a specific card
  path('card/update/<str:uid>', views.card_update, name='card_update'),  # Update an existing card
  path('card/delete/<str:uid>', views.card_delete, name='card_delete'),  # Delete a card
  
  path('device/list', views.device_list, name='device_list'),  # List all devices
  path('device/create', views.device_create, name='device_create'),  # Create a new device
  path('device/<str:id>', views.device_detail, name='device_detail'),  # Detail view for a specific device
  path('device/update/<str:id>', views.device_update, name='device_update'),  # Update an existing device
  path('device/delete/<str:id>', views.device_delete, name='device_delete'),  # Delete a device
  
  path('lock/list', views.lock_list, name='lock_list'),  # List all locks
  path('lock/create', views.lock_create, name='lock_create'),  # Create a new lock
  path('lock/<int:id>', views.lock_detail, name='lock_detail'),  # Detail view for a specific lock
  path('lock/update/<int:id>', views.lock_update, name='lock_update'),  # Update an existing lock
  path('lock/delete/<int:id>', views.lock_delete, name='lock_delete'),  # Delete a lock
]