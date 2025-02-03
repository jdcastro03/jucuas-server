from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from django_extensions.db.models import TimeStampedModel

from deadline.models import Deadline
from presenter.models import Presenter

# Create your models here.
AREA_KNOWLEDGE_CHOICES = (
    ('I', 'I. Físico-Matemáticas y Ciencias de la Tierra'),
    ('II', 'II. Biología y Química'),
    ('III', 'III. Medicina y Ciencias de la Salud'),
    ('IV', 'IV. Ciencias de la Conducta y la Educación'),
    ('V', 'V. Humanidades'),
    ('VI', 'VI. Ciencias Sociales'),
    ('VII', 'VII. Ciencias de la Agricultura, Agropecuarias, Forestales y de Ecosistemas'),
    ('VIII', 'VIII. Ingenierías y Desarrollo Tecnológico'),
    ('IX', 'IX. Investigación Multidisciplinaria'),
)

EDUCATIONAL_LEVEL_TO_IS_DIRECTED_CHOICES = (
    ('PCO', 'Público en general'),
    ('PREESC', 'Preescolar'),
    ('PRIM', 'Primaria'),
    ('SEC', 'Secundaria'),
    ('MDSUP', 'Media superior'),
    ('SUP', 'Superior'),
)

TYPE_OF_PUBLIC_CHOICES = (
    ('INT', 'Interno'), #Interno: estudiantes y personal de la institución
    ('EXT', 'Externo'), #Externo: estudiantes de otras instituciones o público en general
)

EVIDENCE_STATUS = (
    ('SEND', 'Subido'),
    ('DUE', 'Pendiente'),
    ('INC', 'Incompleto'),
    ('REJECT', 'Rechazado'),
    ('OK', 'Aprobado'),
)

ACTIVITY_STATUS = (
    ('DUE', 'Pendiente'),
    ('INC', 'Incompleto'),
    ('REJECT', 'Rechazado'),
    ('OK', 'Aprobado'),
)

#Funcion para subir archivo de evidencia validando la extension que sea pdf, txt o imagen
def upload_evidence_file(instance, filename):
    x = filename.split('.')
    if(x.pop() not in ('pdf','jpg','txt','jpeg','png')):
        raise ValidationError('Extension de archivo invalida.')
    return f'evidence/document/{instance.activity.presenter.id}/{instance.activity.id}/{filename}'

#Funcion para subir archivo de constancia validando la extension que sea pdf
def upload_certificate_file(instance, filename):
    x = filename.split('.')
    if(x.pop() not in ('pdf')):
        raise ValidationError('Extension de archivo invalida.')
    return f'activity/document/certificate/{instance.presenter.id}/{instance.id}/{filename}'

# Modelo tipo de evidencia
class TypeEvidence(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='Nombre')
    type = models.CharField(
        blank=True,
        null=True,
        max_length=6,
        choices=(
            ('PDF', 'PDF'),
            ('URL', 'URL'),
        )
    )
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)
    is_optional = models.BooleanField(verbose_name='Opcional', default=False)

    def __str__(self):
        return '%s' % (self.name)

# Modelo de tipos de actividad
class TypeActivity(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='Nombre')
    title = models.CharField(max_length=800, blank=True, null=True, verbose_name='Titulo')
    maxCopresenter = models.CharField(max_length=100, blank=True, null=True, verbose_name="Maximo de copresentadores")
    type_evidence = models.ManyToManyField(TypeEvidence, related_name='type_evidence')
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)

    def __str__(self):
        return '%s' % (self.name)

# Modelo de actividades
# PONER SI LA ACTIVIDAD CORRESPONDE O NO A LA JORNADA
class Activity(TimeStampedModel):
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='Nombre')
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name='Descripción')
    numbers_expected_attendees = models.PositiveIntegerField(null=True, blank=True,verbose_name='Numero de asistentes esperados')
    numbers_total_attendees = models.PositiveIntegerField(null=True, blank=True,verbose_name='Numero de asistentes totales')
    modality = models.CharField(
        blank=True,
        null=True,
        max_length=1,
        choices=(
            ('V', 'Virtual'),
            ('P', 'Presencial'),
            ('H', 'Hibrida (Virtual y Presencial)')
        )
    )
    edition = models.ForeignKey(Deadline, blank=True, null=False, on_delete=models.CASCADE, default=1)
    date_activity = models.DateTimeField(blank=True)
    educational_level_to_is_directed = models.CharField(blank=True, null=True, max_length=6, choices=EDUCATIONAL_LEVEL_TO_IS_DIRECTED_CHOICES)
    type_of_public = models.CharField(blank=True, null=True, max_length=6, choices=TYPE_OF_PUBLIC_CHOICES)
    area_knowledge = models.CharField(blank=False, null=True, max_length=6, choices=AREA_KNOWLEDGE_CHOICES)
    #activity_manager = models.ForeignKey(ActivityManager, blank=True, null=True, on_delete=models.CASCADE)
    presenter = models.ForeignKey(Presenter, related_name='activity_presenter', blank=True, null=False, on_delete=models.CASCADE)
    #(poner un nuevo max de co-presentadoresy tienes que darle a un check, es un presentador dado de alta: "no recuerdo que era esto ultimo")
    co_presenter = models.ManyToManyField(Presenter, blank=True, related_name='co_presenter')
    type = models.ForeignKey(TypeActivity, blank=True, null=False, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    certificate_file = models.FileField(upload_to=upload_certificate_file, verbose_name="Archivo", blank=True, null=True)
    activity_status = models.CharField(blank=False, null=True, max_length=6, choices=ACTIVITY_STATUS, default='DUE')
    is_active = models.BooleanField(verbose_name='Activo', default=True)
    status = models.BooleanField(verbose_name='Estatus', default=True)
    def __str__(self):
        if self.presenter:
            return '%s - %s - %s' % (self.name, self.type, self.presenter.first_name)
        else:
            return '%s - %s - %s' % (self.name, self.type, "Sin presentador")
# Modelo de evidencias
class Evidence(TimeStampedModel):
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='Nombre')
    observation = models.CharField(max_length=1500, blank=True, null=True, verbose_name='Observación')
    evidence_file = models.FileField(upload_to=upload_evidence_file, verbose_name="Archivo", blank=True, null=True)
    evidence_status = models.CharField(blank=False, null=True, max_length=6, choices=EVIDENCE_STATUS, default='DUE')
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='related_evidence_created_by')
    status_changed_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='related_evidence_status_changed_by')
    type_evidence = models.ForeignKey(TypeEvidence, blank=True, null=True, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, blank=True, null=True, on_delete=models.CASCADE, related_name='related_evidences', verbose_name='Actividad')
    def __str__(self):
        if self.activity.presenter:
            return '%s_%s_%s' % (self.activity.presenter.first_name, self.type_evidence.name, self.evidence_status)
        else:
            return '%s_%s_%s' % ("Sin presentador", self.type_evidence.name, self.evidence_status)
    class Meta:
        unique_together = ('activity', 'type_evidence',)