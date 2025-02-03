from datetime import datetime
from django.db import models


# Create your models here.
# Modelo de fechas limite
class Deadline(models.Model):
    name_edition = models.CharField(max_length=150, blank=True, null=True, verbose_name='Nombre de la edicion')
    date_edition = models.CharField(blank=True, max_length=4)
    date_to_upload_activities = models.DateField(blank=True, null=True)
    date_to_upload_evidence = models.DateField(blank=True, null=True)
    date_to_validate_evidence = models.DateField(blank=True, null=True)
    date_edition_start = models.DateField(blank=True, null=True)
    end_date_of_the_edition = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)
    file = models.TextField(blank=True, null=True)
    file_name = models.CharField(max_length=150, blank=True, null=True)
    def __str__(self):
        return '%s - %s' % (self.name_edition, self.date_edition)