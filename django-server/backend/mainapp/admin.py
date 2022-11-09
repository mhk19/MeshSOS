from django.contrib import admin
from . models import request_logs, UserProfile

admin.site.register(request_logs)
admin.site.register(UserProfile)
