from django.urls import path

from webapp import views

urlpatterns = [
  path('auth', views.authorize, name='auth'),
  path('report/<str:name>', views.report, name='report'),
  
  path('card/list', views.card_list, name='card_list'),  # List all cards
  path('card/create', views.card_create, name='card_create'),  # Create a new card
  path('card/<str:uuid>', views.card_detail, name='card_detail'),  # Detail view for a specific card
  path('card/update/<str:uuid>', views.card_update, name='card_update'),  # Update an existing card
  path('card/delete/<str:uuid>', views.card_delete, name='card_delete'),  # Delete a card
  
  path('device/list', views.device_list, name='device_list'),  # List all devices
  path('device/create', views.device_create, name='device_create'),  # Create a new device
  path('device/<str:id>', views.device_detail, name='device_detail'),  # Detail view for a specific device
  path('device/update/<str:id>', views.device_update, name='device_update'),  # Update an existing device
  path('device/delete/<str:id>', views.device_delete, name='device_delete'),  # Delete a device
  
  path('lock/list', views.lock_list, name='lock_list'),  # List all locks
  path('lock/create', views.lock_create, name='lock_create'),  # Create a new lock
  path('lock/<str:name>', views.lock_detail, name='lock_detail'),  # Detail view for a specific lock
  path('lock/update/<str:name>', views.lock_update, name='lock_update'),  # Update an existing lock
  path('lock/delete/<str:name>', views.lock_delete, name='lock_delete'),  # Delete a lock
  
  path('lock/group/list', views.group_lock_list, name='group_lock_list'),  # List all lock groups
  path('lock/group/create', views.group_lock_create, name='group_lock_create'),  # Create a new lock group
  path('lock/group/<str:name>', views.group_lock_detail, name='group_lock_detail'),  # Detail view for a specific lock group
  path('lock/group/update/<str:name>', views.group_lock_update, name='group_lock_update'),  # Update an existing lock group
  path('lock/group/delete/<str:name>', views.group_lock_delete, name='group_lock_delete'),  # Delete a lock group
  
  path('user/list', views.user_list, name='user_list'),  # List all users
  path('user/create', views.user_create, name='user_create'),  # Create a new user
  path('user/<str:username>', views.user_detail, name='user_detail'),  # Detail view for a specific user
  path('user/update/<str:username>', views.user_update, name='user_update'),  # Update an existing user
  path('user/delete/<str:username>', views.user_delete, name='user_delete'),  # Delete a user
  
  path('user/group/list', views.group_user_list, name='group_user_list'),  # List all user groups
  path('user/group/create', views.group_user_create, name='group_user_create'),  # Create a new user group
  path('user/group/<str:name>', views.group_user_detail, name='group_user_detail'),  # Detail view for a specific user group
  path('user/group/update/<str:name>', views.group_user_update, name='group_user_update'),  # Update an existing user group
  path('user/group/delete/<str:name>', views.group_user_delete, name='group_user_delete'),  # Delete a user group
]