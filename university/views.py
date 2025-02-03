from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common.decorators.auth_decorator import group_required
from django.utils.decorators import method_decorator

from .models import OrganizationalUnit, University
from .serializers import OrganizationalUnitSerializer, UniversitySerializer

from .paginations import CustomPagination

# vista Universidades
class UniversityViewSet(viewsets.ModelViewSet):
    serializer_class = UniversitySerializer

    #lista de las Universidades
    def get_queryset(self):
        return University.objects.filter(status=True)
    
    #elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


# vista Universidades
class UniversityListViewSet(viewsets.ModelViewSet):
    serializer_class = UniversitySerializer
    pagination_class = CustomPagination

    # lista de las Universidades
    def get_queryset(self):
        return University.objects.filter(status=True)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()

# vista de Unidades Organizacionales
class OrganizationalUnitViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationalUnitSerializer

    #lista de las de Unidades Organizacionales
    def get_queryset(self):
        return OrganizationalUnit.objects.filter(status=True)
    
    #elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()