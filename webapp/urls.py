from django.urls import path

from webapp import views

urlpatterns = [
  path('auth', views.auth, name='auth'),
  
  path('booking', views.booking, name='booking'),

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
  
  path('group/list', views.group_list, name='group_list'),  # List all groups
  path('group/create', views.group_create, name='group_create'),  # Create a new group
  path('group/<int:id>', views.group_detail, name='group_detail'),  # Detail view for a specific group
  path('group/update/<int:id>', views.group_update, name='group_update'),  # Update an existing group
  path('group/delete/<int:id>', views.group_delete, name='group_delete'),  # Delete a group
  
  path('lock/list', views.lock_list, name='lock_list'),  # List all locks
  path('lock/create', views.lock_create, name='lock_create'),  # Create a new lock
  path('lock/<int:id>', views.lock_detail, name='lock_detail'),  # Detail view for a specific lock
  path('lock/update/<int:id>', views.lock_update, name='lock_update'),  # Update an existing lock
  path('lock/delete/<int:id>', views.lock_delete, name='lock_delete'),  # Delete a lock
  
  path('user/list', views.user_list, name='user_list'),  # List all users
  path('user/create', views.user_create, name='user_create'),  # Create a new user
  path('user/<int:id>', views.user_detail, name='user_detail'),  # Detail view for a specific user
  path('user/update/<int:id>', views.user_update, name='user_update'),  # Update an existing user
  path('user/delete/<int:id>', views.user_delete, name='user_delete'),  # Delete a user
]