from django.contrib import admin

from webapp.models import Device
from webapp.models import Lock
from webapp.models import Card
from webapp.models import User
from webapp.models import Role
from webapp.models import Record

admin.site.register(Device)
admin.site.register(Lock)
admin.site.register(Card)
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Record)