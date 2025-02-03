from accounts.serializers import UserSerializer
from rest_framework import serializers
from drf_base64.fields import Base64FileField

from deadline.serializers import DeadlineSerializer
from .models import TypeEvidence, TypeActivity, Activity, Evidence
from presenter.serializers import PresenterSerializer, PresenterConstancySerializer

#Serializador de Evidencias
class EvidenceSerializer(serializers.ModelSerializer):
    evidence_file = Base64FileField(allow_null = True)

    class Meta:
        model = Evidence
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['type_evidence'] = TypeEvidenceSerializer(instance.type_evidence).data #Regresa los tipos de evidencia serializadas
        return response

#Serializador de Actividades
class ActivitySerializer(serializers.ModelSerializer):
    evidences = EvidenceSerializer(source='related_evidences', many=True)

    class Meta:
        model = Activity
        exclude = ('status', 'created', 'modified')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['type'] = TypeActivitySerializer(instance.type).data #Regresa los tipos de actividad serializadas
        response['created_by'] = UserSerializer(instance.created_by).data
        response['presenter'] = PresenterSerializer(instance.presenter).data
        response['edition'] = DeadlineSerializer(instance.edition).data
        return response

#Serializador de Actividades para la constancia
class ActivityConstancySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ('name', 'type', 'presenter', 'co_presenter', 'edition')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['type'] = TypeActivityConstancySerializer(instance.type).data #Regresa los tipos de actividad serializadas
        response['presenter'] = PresenterConstancySerializer(instance.presenter).data
        response['co_presenter'] = PresenterConstancySerializer(instance.co_presenter, many=True).data
        return response

#SOLO PARA CREAR Serializador de Actividades
class CreateActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        exclude = ('status', 'created', 'modified')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['type'] = TypeActivitySerializer(instance.type).data #Regresa los tipos de actividad serializadas
        response['created_by'] = UserSerializer(instance.created_by).data
        response['edition'] = DeadlineSerializer(instance.edition_id).data
        return response

#Serializador de Tipos de actividades
class TypeActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeActivity
        exclude = ('status',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['type_evidence'] = TypeEvidenceSerializer(instance.type_evidence, many=True).data #Regresa los tipos de evidencia serializadas
        return response

#Serializador de Tipos de actividades para la constancia
class TypeActivityConstancySerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeActivity
        fields = ('title',)

#Serializador de Tipos de evidencia
class TypeEvidenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeEvidence
        exclude = ('status',)