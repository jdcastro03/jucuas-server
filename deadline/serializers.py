from rest_framework import serializers
from .models import Deadline

#Serializador de fechas de la jornada universitaria
class DeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deadline
        exclude = ('status',)