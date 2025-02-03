from django.db import models
from django.conf import settings

from university.models import University, OrganizationalUnit

# Modelo de Representantes
class Representative(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='representative_user', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Nombre')
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Apellido')
    user_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Usuario')
    origin_university = models.ForeignKey(University, blank=True, null=True, on_delete=models.CASCADE, default=None)
    origin_organizational_unit = models.ForeignKey(OrganizationalUnit, blank=True, null=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name='Correo')
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

