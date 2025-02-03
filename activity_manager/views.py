from rest_framework import viewsets
from common.decorators.auth_decorator import group_required
from django.utils.decorators import method_decorator
from .models import ActivityManager
from .serializers import ActivityManagerSerializer

# vista Responsable de actividad
@method_decorator(group_required('admin') , name='dispatch')
class ActivityManagerViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityManagerSerializer

    #lista de los Responsables de actividad
    def get_queryset(self):
        return ActivityManager.objects.filter(status=True)
    
    #elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()