from django.contrib import admin

from webapp.models import CustomGroup
from webapp.models import Card
from webapp.models import Device
from webapp.models import Lock
from webapp.models import Record

admin.site.register(CustomGroup)
admin.site.register(Card)
admin.site.register(Device)
admin.site.register(Lock)
admin.site.register(Record)