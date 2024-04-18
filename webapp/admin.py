from django.contrib import admin

from webapp.models import Card
from webapp.models import Device
from webapp.models import Group
from webapp.models import Lock
from webapp.models import Record
from webapp.models import User

admin.site.register(Card)
admin.site.register(Device)
admin.site.register(Group)
admin.site.register(Lock)
admin.site.register(Record)
admin.site.register(User)