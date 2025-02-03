from django.db import models
from django.conf import settings

# Modelo de Responsable de actividad
class ActivityManager(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='activity_manager_user', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Nombre')
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Apellido')
    gender = models.CharField(
        blank=True,
        null=True,
        max_length=1,
        choices=(
            ('M', 'Mujer'),
            ('H', 'Hombre'),
            ('O', 'Otro'),
        )
    )
    academic_degree = models.CharField(
        blank=True,
        null=True,
        max_length=1,
        choices=(
            ('L', 'Licenciatura'),
            ('M', 'Maestria'),
            ('D', 'Doctorado'),
        )
    )
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name='Correo')
    birth_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)