from datetime import datetime

from rest_framework import serializers
from django.contrib.auth.models import Group
from accounts.models import User

from university.serializers import OrganizationalUnitSerializer, UniversitySerializer
from .models import Representative

#Serializador de los Representantes
class RepresentativeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Representative
        exclude = ('status',)

    def get_from_user_id(id):return Representative.objects.filter(user=id).only('phone', 'gender')

    def create(self, validated_data):
        representative = Representative.objects.create(**validated_data)

        user = User(
            username = representative.user_name,
            email = representative.email
        )
        contra = f'JUCUAS{datetime.now().date().year}'
        user.set_password(contra)
        user.save()
        group_representative = Group.objects.get(name='representative')
        group_representative.user_set.add(user)
        representative.user = user
        representative.save()

        return representative

    def update(self, instance, validated_data):
        user = User.objects.get(username=validated_data.get('user'))

        instance.origin_university = validated_data.get('origin_university', instance.origin_university)
        instance.origin_organizational_unit = validated_data.get('origin_organizational_unit', instance.origin_organizational_unit)

        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('user_name'):
            instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        user.email = instance.email
        if validated_data.get('user_name'):
            user.username = instance.user_name
        user.save()

        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['origin_university'] = UniversitySerializer(instance.origin_university).data #Regresa las universidades serializadas
        response['origin_organizational_unit'] = OrganizationalUnitSerializer(instance.origin_organizational_unit).data #Regresa las unidades organizacionales serializadas
        return response
