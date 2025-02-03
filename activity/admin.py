from django.contrib import admin

from .models import Activity, TypeActivity, Evidence, TypeEvidence

admin.site.register(Activity)
admin.site.register(TypeActivity)
admin.site.register(Evidence)
admin.site.register(TypeEvidence)