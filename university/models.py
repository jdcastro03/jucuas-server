from django.db import models

# Modelo de Universidades
class University(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='Nombre')
    acronym = models.CharField(max_length=10, blank=True, null=True, verbose_name='Siglas')
    key_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Clave')
    type = models.CharField(
        blank=True,
        null=True,
        max_length=6,
        choices=(
            ('PREESC', 'Preescolar'),
            ('PRIM', 'Primaria'),
            ('SEC', 'Secundaria'),
            ('P', 'Preparatoria'),
            ('U', 'Universidad'),
        )
    )
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
    municipality = models.CharField(max_length=150, blank=True, null=True, verbose_name='Municipio')
    locality = models.CharField(max_length=150, blank=True, null=True, verbose_name='Localidad')
    email = models.CharField(max_length=150, blank=True, null=True, verbose_name='Correo')
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name='Telefono')
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ('name',)

# Modelo de Unidades Organizacionales
class OrganizationalUnit(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='Nombre')
    acronym = models.CharField(max_length=10, blank=True, null=True, verbose_name='Siglas')
    key_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Clave')
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
    municipality = models.CharField(max_length=150, blank=True, null=True, verbose_name='Municipio')
    locality = models.CharField(max_length=150, blank=True, null=True, verbose_name='Localidad')
    email = models.CharField(max_length=150, blank=True, null=True, verbose_name='Correo')
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name='Telefono')
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ('name',)
