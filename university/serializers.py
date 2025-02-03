from rest_framework import serializers
from .models import OrganizationalUnit, University

#Serializador de las Universidades
class UniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = University
        exclude = ('status',)

#Serializador de las Unidades Organizacionales
class OrganizationalUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationalUnit
        exclude = ('status',)