from django.contrib import admin

from webapp.models import AccessRecord
from webapp.models import ActivityRecord
from webapp.models import Card
from webapp.models import LockGroup
from webapp.models import UserGroup
from webapp.models import Device
from webapp.models import Lock

admin.site.register(AccessRecord)
admin.site.register(ActivityRecord)
admin.site.register(Card)
admin.site.register(LockGroup)
admin.site.register(UserGroup)
admin.site.register(Device)
admin.site.register(Lock)