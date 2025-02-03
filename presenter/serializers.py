from rest_framework import serializers
from django.contrib.auth.models import Group
from accounts.models import User
from datetime import datetime
from university.serializers import OrganizationalUnitSerializer, UniversitySerializer
from .models import Presenter


# Serializador de los Presentadores
class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        exclude = ('status',)

    def get_from_user_id(id):
        return Presenter.objects.filter(user=id).only('phone', 'gender')

    # deprecated :v
    # def get_phone(self):return Presenter.phone
    def create(self, validated_data):
        presenter = Presenter.objects.create(**validated_data)

        # EL USERNAME VA A SER EL EMAIL
        user = User(
            username=presenter.email,
            email=presenter.email
        )
        contra = f'JUCUAS{datetime.now().date().year}'
        user.set_password(contra)
        user.username = presenter.email
        user.save()
        group_presenter = Group.objects.get(name='presenter')
        group_presenter.user_set.add(user)
        presenter.user = user
        presenter.save()

        return presenter

    def update(self, instance, validated_data):
        user = User.objects.get(username=validated_data.get('user'))
        instance.origin_university = validated_data.get('origin_university', instance.origin_university)
        instance.origin_organizational_unit = validated_data.get('origin_organizational_unit',
                                                                 instance.origin_organizational_unit)
        instance.if_belong_to_school = validated_data.get('if_belong_to_school', instance.if_belong_to_school)

        if instance.if_belong_to_school:
            # hace falta mandar la unidad a la que pertenece el representante
            pass

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.curp = validated_data.get('curp', instance.curp)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.academic_degree = validated_data.get('academic_degree', instance.academic_degree)
        instance.position_institution = validated_data.get('position_institution', instance.position_institution)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.status = validated_data.get('status', instance.status)


        if user.email == validated_data.get('email', instance.email):
            user.email = validated_data.get('email', instance.email)
            user.username = validated_data.get('email', instance.email)
            user.save()
            instance.user_name = validated_data.get('user_name', instance.email)

        instance.save()
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['origin_university'] = UniversitySerializer(
            instance.origin_university).data  # Regresa las universidades serializadas
        response['origin_organizational_unit'] = OrganizationalUnitSerializer(
            instance.origin_organizational_unit).data  # Regresa las unidades organizacionales serializadas
        return response


# Serializador de los Presentadores para la constancia
class PresenterConstancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = ('full_name_academic',)


class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = ('phone', 'email', 'curp',)