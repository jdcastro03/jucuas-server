from presenter.models import Presenter
from representative.models import Representative
from rest_framework import serializers
from django.contrib.auth.models import Group

from reviewer.models import Reviewer

from .models import User

class UserSerializer(serializers.ModelSerializer):
	
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'is_active', 'is_superuser')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['groups'] = GroupsSerializer(instance.groups, many=True).data #regresa los grupos serializados
        
        if response['groups'][0]['name'] == 'representative':
            representative = Representative.objects.get(user_id = instance.id)
            response['first_name'] = representative.first_name
            response['last_name'] = representative.last_name
            if representative.origin_university:
                response['origin_university'] = representative.origin_university.name
            if representative.origin_organizational_unit:
                response['origin_organizational_unit'] = representative.origin_organizational_unit.name

        elif response['groups'][0]['name'] == 'presenter':
            presenter = Presenter.objects.get(user_id = instance.id)
            response['first_name'] = presenter.first_name
            response['last_name'] = presenter.last_name
            if presenter.origin_university:
                response['origin_university'] = presenter.origin_university.name
            if presenter.origin_organizational_unit:
                response['origin_organizational_unit'] = presenter.origin_organizational_unit.name

        elif response['groups'][0]['name'] == 'reviewer':
            reviewer = Reviewer.objects.get(user_id = instance.id)
            response['first_name'] = reviewer.first_name
            response['last_name'] = reviewer.last_name

            response['region'] = reviewer.region
            response['global_reviewer'] = reviewer.global_reviewer

            if reviewer.origin_university:
                response['origin_university'] = reviewer.origin_university.name
            if reviewer.origin_organizational_unit:
                response['origin_organizational_unit'] = reviewer.origin_organizational_unit.name
            
        return response

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)