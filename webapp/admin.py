from django.contrib import admin

from webapp.models import AccessRecord
from webapp.models import ActivityRecord
from webapp.models import Card
from webapp.models import CustomGroup
from webapp.models import Device
from webapp.models import Lock

admin.site.register(AccessRecord)
admin.site.register(ActivityRecord)
admin.site.register(Card)
admin.site.register(CustomGroup)
admin.site.register(Device)
admin.site.register(Lock)