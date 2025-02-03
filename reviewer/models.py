from django.db import models
from django.conf import settings

from university.models import University, OrganizationalUnit

# Modelo de Revisadores
class Reviewer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='reviewer_user', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Nombre')
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Apellido')
    user_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Usuario')
    region = models.CharField(
        blank=True,
        null=True,
        max_length=2,
        choices=(
            ('N', 'Norte'),
            ('CN', 'Centro Norte'),
            ('C', 'Centro'),
            ('S', 'Sur'),
        )
    )
    global_reviewer = models.BooleanField(verbose_name='Revisor general', default=False)
    origin_university = models.ForeignKey(University, blank=True, null=True, on_delete=models.CASCADE)
    origin_highschool = models.ForeignKey(University, blank=True, null=True, on_delete=models.CASCADE, related_name="origin_highschool")
    origin_organizational_unit = models.ForeignKey(OrganizationalUnit, blank=True, null=True, on_delete=models.CASCADE)
    reviewer_permission = models.CharField(max_length=10, blank=True, null=True, verbose_name='Permisos')
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name='Correo')
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)