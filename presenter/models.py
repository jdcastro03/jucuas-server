from django.db import models
from django.conf import settings
from accounts.models import User

from university.models import OrganizationalUnit, University

POSITION_INSTITUTION_CHOICES = (
    ('1','Estudiante'),
    ('2','Maestro'),
    ('3','Director'),
    ('4','Personal de confianza'),
    ('5','Externo'),
)

# Modelo de Presentadores
#MODIFICAR LA CONEXION ENTRE PRESENTADOR, ACTIVIDAD Y EVIDENCIA
#AGREGAR EL REPRESENTANTE/USUARIO QUE LO DA DE ALTA
class Presenter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='presenter_user', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Nombre')
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Apellido')
    user_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Usuario')
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
    curp = models.CharField(max_length=18, blank=True, null=True, verbose_name="Curp")
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name='Correo')
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name='Telefono')
    academic_degree = models.CharField(max_length=50, blank=True, null=True, verbose_name='Grado Academico')
    origin_university = models.ForeignKey(University, blank=True, null=True, on_delete=models.CASCADE)
    origin_organizational_unit = models.ForeignKey(OrganizationalUnit, blank=True, null=True, on_delete=models.CASCADE)
    if_belong_to_school = models.BooleanField(verbose_name='Pertenece a la misma unidad academica/organizacional', default=True)
    position_institution = models.CharField(max_length=2, choices=POSITION_INSTITUTION_CHOICES, default='1')
    birth_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return self.full_name_academic

    @property
    def full_name_academic(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Meta:
        ordering = ('first_name', 'last_name')
