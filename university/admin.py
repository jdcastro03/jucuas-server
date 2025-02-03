from django.contrib import admin

from .models import OrganizationalUnit, University

admin.site.register(University)
admin.site.register(OrganizationalUnit)
