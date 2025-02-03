from rest_framework import serializers
from .models import ActivityManager

#Serializador de Responsable de actividad
class ActivityManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityManager
        exclude = ('status',)