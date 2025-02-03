import base64
import datetime
import time
from datetime import date
from dotenv import load_dotenv
import os
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Q, Value
from io import BytesIO
from rest_framework import status, viewsets
from rest_framework import status as sts
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.templatetags import rest_framework
from rest_framework.views import APIView
import qrcode
from PIL import Image
import jwt
from django.db.models.functions import Concat
from activity.SQLConnector import SQLConnector
from deadline.models import Deadline
from deadline.serializers import DeadlineSerializer
from presenter.models import Presenter
from presenter.serializers import PresenterSerializer
from representative.serializers import RepresentativeSerializer
from reviewer.serializers import ReviewerSerializer
from university.serializers import UniversitySerializer, OrganizationalUnitSerializer
from .paginations import CustomPagination
from accounts.serializers import GroupsSerializer
from .models import TypeEvidence, TypeActivity, Activity, Evidence
from reviewer.models import Reviewer
from representative.models import Representative
from activity.serializers import TypeEvidenceSerializer, TypeActivitySerializer, ActivitySerializer, \
    CreateActivitySerializer, EvidenceSerializer, ActivityConstancySerializer
from deadline.views import current_date_to_upload_activities, current_date_to_upload_evidences, \
    current_date_to_validate_evidences
from common.decorators.auth_decorator import group_required
from django.core import serializers
from django.forms.models import model_to_dict
from django.db import connection
from university.models import University, OrganizationalUnit

from decouple import config

load_dotenv()

host = os.environ['DATABASE_HOST']
db = os.environ['DATABASE_NAME']
user = os.environ['DATABASE_USER']
password = os.environ['DATABASE_PASSWORD']

con = SQLConnector(host=host, db=db, port="3306", user=user, password=password)
con.connect()

# vista de Actividades


@method_decorator(group_required('admin', 'representative', 'reviewer'), name='dispatch')
class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    pagination_class = CustomPagination

    # lista de las actividades
    def get_queryset(self):
        group = GroupsSerializer(self.request.user.groups, many=True).data
        if group[0]['name'] == 'reviewer':
            user = ReviewerSerializer(Reviewer.objects.filter(
                user_id=self.request.user.id), many=True).data
            edicion = Deadline.objects.all().last()
            permission = user[0]['reviewer_permission']
            # Todos, debido a que es global
            if user[0]['global_reviewer']:
                return Activity.objects.filter(edition=edicion, status=True)
            else:
                region = ''
                if 'N' in permission:
                    region = 'N'
                if 'X' in permission:
                    region = 'CN'
                if 'C' in permission:
                    region = 'C'
                if 'S' in permission:
                    region = 'S'
                actividades = None
                print(region)
                if 'O' in permission:
                    print("ORG")
                    representatives_o = [rr.user.id for rr in Representative.objects.filter(
                        Q(origin_organizational_unit__region=region))]
                    actividades_o = Activity.objects.filter(
                        edition=edicion, status=True, created_by__pk__in=representatives_o, presenter__isnull=False
                    )
                    if actividades == None:
                        actividades = actividades_o
                    else:
                        actividades = actividades | actividades_o
                if 'U' in permission:
                    print("UNI")
                    representatives_u = [rr.user.id for rr in Representative.objects.filter(
                        Q(origin_university__region=region) & Q(origin_university__type="U"))]
                    actividades_u = Activity.objects.filter(
                        edition=edicion, status=True, created_by__pk__in=representatives_u, presenter__isnull=False
                    )
                    print(actividades_u)
                    if actividades == None:
                        actividades = actividades_u
                    else:
                        actividades = actividades | actividades_u
                if 'P' in permission:
                    print("PREPA")
                    representatives_p = [rr.user.id for rr in Representative.objects.filter(
                        Q(origin_university__region=region) & Q(origin_university__type="P"))]
                    actividades_p = Activity.objects.filter(
                        edition=edicion, status=True, created_by__pk__in=representatives_p, presenter__isnull=False
                    )
                    if actividades == None:
                        actividades = actividades_p
                    else:
                        actividades = actividades | actividades_p
                return actividades
        else:
            return Activity.objects.filter(status=True)

    # elimina la instancia recibida

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


@api_view(['POST'])
def get_filteredlisttable(request):
    filter = request.data.get('filter')
    form = request.data.get('form')
    pepe = GroupsSerializer(request.user.groups, many=True).data
    group = pepe[0]['name']
    page = int(request.GET['p'])
    page_size = int(request.GET['page_size'])
    offset = page * page_size - page_size
    limit = offset + page_size
    data = []
    next = None
    previous = None
    count = 0

    if group == 'admin':
        queryset = Activity.objects.annotate(search_name=Concat(
            'presenter__first_name', Value(' '), 'presenter__last_name'))
        if form == 'activities':
            count = queryset.filter(
                Q(search_name__icontains=filter) |
                Q(name__icontains=filter) | Q(type__name__icontains=filter) | Q(
                    presenter__origin_university__name__icontains=filter) | Q(
                    presenter__origin_organizational_unit__name__icontains=filter) | Q(
                    edition__date_edition__icontains=filter), status=True).count()
            data = ActivitySerializer(queryset.filter(
                Q(search_name__icontains=filter) |
                Q(name__icontains=filter) | Q(type__name__icontains=filter) | Q(
                    presenter__origin_university__name__icontains=filter) | Q(
                    presenter__origin_organizational_unit__name__icontains=filter) | Q(
                    edition__date_edition__icontains=filter), status=True)[offset:limit], many=True).data
        else:
            count = queryset.filter(
                Q(search_name__icontains=filter) | Q(name__icontains=filter) |
                Q(edition__date_edition__icontains=filter) |
                Q(type__name__icontains=filter), status=True).count()
            data = ActivitySerializer(queryset.filter(
                Q(search_name__icontains=filter) | Q(name__icontains=filter) |
                Q(edition__date_edition__icontains=filter) |
                Q(type__name__icontains=filter), status=True)[offset:limit], many=True).data
    elif group == 'representative':
        queryset = Activity.objects.annotate(search_name=Concat(
            'presenter__first_name', Value(' '), 'presenter__last_name'))
        edicion = DeadlineSerializer(Deadline.objects.all().last()).data
        if form == 'activities':
            count = queryset.filter(Q(search_name__icontains=filter) |
                                    Q(name__icontains=filter) | Q(type__name__icontains=filter) | Q(
                presenter__origin_university__name__icontains=filter) | Q(
                presenter__origin_organizational_unit__name__icontains=filter),
                                    created_by=request.user, edition=edicion['id'], status=True).count()
            data = ActivitySerializer(queryset.filter(Q(search_name__icontains=filter) |
                                                      Q(name__icontains=filter) | Q(type__name__icontains=filter) | Q(
                presenter__origin_university__name__icontains=filter) | Q(
                presenter__origin_organizational_unit__name__icontains=filter),
                                                      created_by=request.user, edition=edicion['id'], status=True)[
                                      offset:limit], many=True).data
        else:
            count = queryset.filter(Q(search_name__icontains=filter) |
                                    Q(name__icontains=filter) | Q(edition__date_edition__icontains=filter) |
                                    Q(type__name__icontains=filter),
                                    created_by=request.user, edition=edicion['id'], status=True).count()
            data = ActivitySerializer(queryset.filter(Q(search_name__icontains=filter) |
                                                      Q(name__icontains=filter) | Q(
                edition__date_edition__icontains=filter) |
                                                      Q(type__name__icontains=filter),
                                                      created_by=request.user, edition=edicion['id'], status=True)[
                                      offset:limit], many=True).data
    elif group == 'presenter':
        user = Presenter.objects.get(user=request.user)
        count = Activity.objects.filter(Q(name__icontains=filter) | Q(type__name__icontains=filter) | Q(
            presenter__origin_university__name__icontains=filter) | Q(
            presenter__origin_organizational_unit__name__icontains=filter) | Q(edition__date_edition__icontains=filter),
                                        presenter=user).count()
        data = ActivitySerializer(Activity.objects.filter(
            Q(name__icontains=filter) | Q(type__name__icontains=filter) | Q(
                presenter__origin_university__name__icontains=filter) | Q(
                presenter__origin_organizational_unit__name__icontains=filter) | Q(
                edition__date_edition__icontains=filter), presenter=user)[offset:limit], many=True).data
    elif group == 'reviewer':
        edicion = DeadlineSerializer(Deadline.objects.all().last()).data
        queryset = Activity.objects.annotate(
            search_name=Concat('presenter__first_name', Value(' '), 'presenter__last_name'))
        user = ReviewerSerializer(Reviewer.objects.filter(
            user_id=request.user.id), many=True).data
        edicion = DeadlineSerializer(Deadline.objects.all().last()).data
        if user[0]['global_reviewer']:
            count = queryset.filter(
                Q(name__icontains=filter) | Q(search_name__icontains=filter) | Q(type__name__icontains=filter),
                edition_id=edicion['id'], status=True).count()
            data = ActivitySerializer(queryset.filter(
                Q(name__icontains=filter) | Q(search_name__icontains=filter) | Q(type__name__icontains=filter),
                edition_id=edicion['id'], status=True), many=True).data
        else:
            region = user[0]['region']
            representatives = [rr.user.id for rr in Representative.objects.filter(
                                Q(origin_organizational_unit__name__icontains=filter) |
                                Q(origin_university__name__icontains=filter)) ]
            print(representatives)
            count = queryset.filter((Q(name__icontains=filter) | Q(search_name__icontains=filter) |
                                     Q(type__name__icontains=filter)),
                                    (Q(presenter__origin_organizational_unit__region=region) |
                                     Q(presenter__origin_university__region=region))
                                    &Q(created_by__pk__in=representatives),
                                    edition_id=edicion['id'], status=True).count()
            data = ActivitySerializer(queryset.filter((Q(name__icontains=filter) | Q(search_name__icontains=filter) |
                                                       Q(type__name__icontains=filter)),
                                                      (Q(presenter__origin_organizational_unit__region=region) |
                                                       Q(presenter__origin_university__region=region))
                                                      &Q(created_by__pk__in=representatives),
                                                      edition_id=edicion['id'], status=True), many=True).data

        '''try:
            count = queryset.filter(Q(name__icontains=filter) | Q(search_name__icontains=filter) | Q(type__name__icontains=filter),
                    edition_id=edicion['id'], created_by__in=users_representative, status=True).count()
            data = ActivitySerializer(
                queryset.filter(Q(name__icontains=filter) | Q(search_name__icontains=filter) | Q(type__name__icontains=filter),
                    edition_id=edicion['id'], created_by__in=users_representative, status=True)[offset:limit], many=True).data
        except Exception as e:
            count = Activity.objects.filter(Q(search_name__icontains=filter) | Q(name__icontains=filter) | Q(type__name__icontains=filter),
                edition_id=edicion['id'], created_by=request.user, status=True).count()
            data = ActivitySerializer(
                Activity.objects.filter(Q(search_name__icontains=filter) | Q(name__icontains=filter) | Q(type__name__icontains=filter),
                edition_id=edicion['id'], created_by=request.user, status=True)[offset:limit], many=True).data'''
    else:
        count = Activity.objects.filter(Q(type__name__icontains=filter) | Q(
            name__icontains=filter), created_by=request.user, status=True).count()
        data = ActivitySerializer(Activity.objects.filter(Q(type__name__icontains=filter) | Q(
            name__icontains=filter), created_by=request.user, status=True)[offset:limit], many=True).data

    if limit < count:
        next = f"activities/filteredlisttable/?p={page + 1}&page_size={page_size}"
    if page > 1:
        previous = f"activities/filteredlisttable/?p={page - 1}&page_size={page_size}"

    response = {
        "count": count,
        "next": next,
        "previous": previous,
        "results": data
    }
    return JsonResponse(response, safe=False)


# SOLO PARA CREAR


@method_decorator(group_required('admin', 'representative'), name='dispatch')
class CreateActivityViewSet(viewsets.ModelViewSet):
    serializer_class = CreateActivitySerializer

    # lista de las actividades
    def get_queryset(self):
        return Activity.objects.filter(status=True)

    def create(self, request, *args, **kwargs):
        group = GroupsSerializer(self.request.user.groups, many=True).data
        if group[0]['name'] == 'representative':
            if not current_date_to_upload_activities():
                return Response({'status': 'Error', 'message': 'La fecha limite para subir actividades ya paso'},
                                status=status.HTTP_400_BAD_REQUEST)
            edicion = DeadlineSerializer(Deadline.objects.all().last()).data
            request.data['edition'] = edicion['id']
        request.data['created_by'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        for value in serializer.data['type']['type_evidence']:
            for k, v in value.items():
                if k == 'id':
                    evidence = Evidence(
                        activity_id=serializer.data['id'], type_evidence_id=v)
                    try:
                        evidence.full_clean()
                    except:
                        print('Error')
                    evidence.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


# partial update para modificar solo el numero de asistentes reales


@method_decorator(group_required('admin', 'representative'), name='dispatch')
class PartialUpdateActivityViewSet(APIView):

    def put(self, request, pk):
        try:
            activity_obj = get_object_or_404(Activity, pk=pk)
            serializer = ActivitySerializer(
                instance=activity_obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)  # Se valida
            serializer.save()  # Se guarda
        except Exception as e:
            print("error: ", e)
            return Response({'status': 'Error', 'message': 'Al modificar el numero de asistentes'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


# partial update para modificar solo el numero de asistentes reales


@method_decorator(group_required('admin', 'reviewer'), name='dispatch')
class PartialUpdateSavePDFActivityViewSet(APIView):

    def put(self, request, pk):
        try:
            data = {}
            activity_obj = get_object_or_404(Activity, pk=pk)
            data['certificate_file'] = ContentFile(base64.b64decode(
                request.data['certificate_file']), name='%s_%s.pdf' % (activity_obj.id, activity_obj.presenter))
            serializer = ActivitySerializer(
                instance=activity_obj, data=data, partial=True)
            serializer.is_valid(raise_exception=True)  # Se valida
            serializer.save()  # Se guarda
        except Exception as e:
            print("error: ", e)
            return Response({'status': 'Error', 'message': 'Problema al guardar el PDF'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


# vista de Actividades por presentador


@method_decorator(group_required('admin', 'representative', 'presenter'), name='dispatch')
class ActivityByPresenterViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    pagination_class = CustomPagination

    # lista de las actividades por presentador
    def get_queryset(self):
        print(self.request.user.groups)
        # queryGroup = f"SELECT g.name FROM accounts_user_groups AS a, auth_group AS g, presenter_presenter AS p WHERE a.group_id = g.id AND p.id = a.user_id AND p.user_id = {self.request.user.id}"
        query = f"SELECT * FROM activity_activity as a JOIN presenter_presenter as p WHERE a.presenter_id = p.id AND p.user_id = {self.request.user.id}"
        return Activity.objects.raw(query)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


# vista de Actividades por usuario


@method_decorator(group_required('admin', 'representative'), name='dispatch')
class ActivityByRepresenterViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    pagination_class = CustomPagination

    # lista de las actividades por usuario
    def get_queryset(self):
        edicion = DeadlineSerializer(Deadline.objects.all().last()).data
        return Activity.objects.filter(created_by=self.request.user, edition_id=edicion['id'], status=True)


# vista de Actividades para constancia


@api_view(['POST'])
@permission_classes([AllowAny])
def ActivityConstansy(request):
    try:
        activity_id = request.data['activity_id']
        activity_obj = Activity.objects.get(id=activity_id)
        serializer = ActivityConstancySerializer(instance=activity_obj).data
        edition = serializer.get('edition')
        edt = Deadline.objects.get(id=edition)
        serialized_edt = serializers.serialize('json', [edt, ])
        dict_edt = model_to_dict(edt)
        print(edition)
        res = {"name": serializer.get('name'),
               "type": serializer.get('type'),
               "presenter": serializer.get('presenter'),
               "co_presenter": serializer.get("co_presenter"),
               "edition": dict_edt
               }
    except Exception as e:
        print("error: ", e)
        return Response({'status': 'Error', 'message': 'Problema al crear el PDF'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'OK', 'message': res}, status=status.HTTP_200_OK)


# vista de Actividades por region del representante
# AUN NO FUNCIONA ARREGLARLO


@method_decorator(group_required('admin', 'reviewer'), name='dispatch')
class ActivityByRegionViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    pagination_class = CustomPagination

    # lista de las actividades por region del representante
    def get_queryset(self):
        edicion = DeadlineSerializer(Deadline.objects.all().last()).data
        group = GroupsSerializer(self.request.user.groups, many=True).data
        if group[0]['name'] == 'reviewer':
            try:
                reviewer = Reviewer.objects.get(user=self.request.user)
                representatives = Representative.objects.filter(Q(origin_university__region=reviewer.region) | Q(
                    origin_organizational_unit__region=reviewer.region))
                users_representative = [r.user for r in representatives]
                return Activity.objects.filter(created_by__in=users_representative, edition_id=['id'], status=True)
            except Exception as e:
                print("error: ", e)
                return Activity.objects.filter(created_by=self.request.user, edition_id=['id'], status=True)
        return Activity.objects.filter(created_by=self.request.user, edition_id=['id'], status=True)


# vista de Evidencias


@method_decorator(group_required('admin'), name='dispatch')
class EvidenceViewSet(viewsets.ModelViewSet):
    serializer_class = EvidenceSerializer
    pagination_class = CustomPagination

    # lista de las evidencias
    def get_queryset(self):
        return Evidence.objects.filter(status=True)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


# vista de EDITAREvidencias #SOLO ADMINISTRADOR Y REPRESENTANTES


@method_decorator(group_required('admin', 'representative'), name='dispatch')
class PartialUpdateEvidenceViewSet(APIView):

    def put(self, request, pk):
        group = GroupsSerializer(self.request.user.groups, many=True).data
        if group[0]['name'] == 'representative':
            if not current_date_to_upload_evidences():
                return Response({'status': 'Error', 'message': 'La fecha limite para subir evidencias ya paso'},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data['evidence_status'] == 'OK':
                return Response(
                    {'status': 'Error', 'message': 'Esta evidencia ya esta aprobada no puedes reemplazarla'},
                    status=status.HTTP_400_BAD_REQUEST)
            if request.data['evidence_status'] == 'REJECT':
                return Response(
                    {'status': 'Error', 'message': 'Esta evidencia ya esta rechazada no puedes reemplazarla'},
                    status=status.HTTP_400_BAD_REQUEST)

        evidence_obj = get_object_or_404(Evidence, pk=pk)
        request.data['created_by'] = self.request.user.id
        request.data['evidence_status'] = 'SEND'
        serializer = EvidenceSerializer(
            instance=evidence_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # Se valida
        serializer.save()  # Se guarda
        return Response(serializer.data, status=status.HTTP_200_OK)


# vista de ValidarEvidencias #SOLO ADMINISTRADOR Y REVISADORES
@method_decorator(group_required('admin', 'reviewer'), name='dispatch')
class PartialValidateEvidenceViewSet(APIView):

    def put(self, request, pk):
        group = GroupsSerializer(self.request.user.groups, many=True).data
        evidence_obj = get_object_or_404(Evidence, pk=pk)
        if group[0]['name'] == 'reviewer':
            if not current_date_to_validate_evidences():
                return Response({'status': 'Error', 'message': 'La fecha limite para validar evidencias ya paso'},
                                status=status.HTTP_400_BAD_REQUEST)
            if evidence_obj.evidence_status == 'OK':
                return Response(
                    {'status': 'Error', 'message': 'Esta evidencia ya esta aprobada no puedes cambiar su estatus'},
                    status=status.HTTP_400_BAD_REQUEST)
            if evidence_obj.evidence_status == 'DUE':
                return Response(
                    {'status': 'Error', 'message': 'No puedes cambiar el estatus de una evidencia que no se a subido'},
                    status=status.HTTP_400_BAD_REQUEST)
            if evidence_obj.evidence_status == 'REJECT':
                return Response(
                    {'status': 'Error', 'message': 'Esta evidencia ya esta rechazada no puedes cambiar su estatus'},
                    status=status.HTTP_400_BAD_REQUEST)

        request.data['status_changed_by'] = self.request.user.id
        serializer = EvidenceSerializer(
            instance=evidence_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # Se valida
        serializer.save()  # Se guarda
        if check_status_of_evidence(evidence_obj.activity_id):
            return Response({'status': 'OK', 'message': 'Se generara la constancia'}, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(group_required('admin'), name='dispatch')
class EvidenceByActivityViewSet(APIView):

    # evidencias por actividad
    def get(self, request, activity_id):
        evidences = Evidence.objects.filter(activity=activity_id)
        serializer = EvidenceSerializer(evidences, many=True)
        return Response(serializer.data)


# vista de Tipos de actividades


class TypeActivityViewSet(viewsets.ModelViewSet):
    serializer_class = TypeActivitySerializer

    # lista de los tipos de actividad
    def get_queryset(self):
        return TypeActivity.objects.filter(status=True)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


# vista de Tipos de evidencia


@method_decorator(group_required('admin'), name='dispatch')
class TypeEvidenceViewSet(viewsets.ModelViewSet):
    serializer_class = TypeEvidenceSerializer

    # lista de los tipos de evidencia
    def get_queryset(self):
        return TypeEvidence.objects.filter(status=True)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


@api_view(['POST'])
@permission_classes([AllowAny])
def qr_generator(request):
    try:
        qr = qrcode.QRCode(version=None, box_size=10, border=4)
        qr.add_data(request.data['data'])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_offset = Image.new('RGB', (1500, 1500), 'white')
        qr_offset.paste(img)
        stream = BytesIO()
        qr_offset.save(stream, 'PNG')
        img_str = base64.b64encode(stream.getvalue()).decode("utf-8")
    except Exception as e:
        print("error: ", e)
        return Response({'status': 'Error', 'message': 'Problema al crear el QR'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'OK', 'message': img_str}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_certificate(request):
    try:
        recipient = []
        activity = Activity.objects.get(id=request.data['activity_id'])
        subject = 'Constancia'
        message = 'En este correo se adjunta su constancia por la participación en la Jornada Universitaria del Conocimiento UAS. Favor de no responder a este mensaje ya que es un envío automatizado y con una bandeja no monitoreada.'
        if activity.presenter.email is not None:
            recipient.append(activity.presenter.email)
        if activity.presenter.created_by.email is not None:
            recipient.append(activity.presenter.created_by.email)
        for co_presenter in activity.co_presenter.all():
            if co_presenter.email is not None:
                recipient.append(co_presenter.email)
        email = EmailMessage(
            subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
        email.attach_file(activity.certificate_file.path)
        email.send()
        # send_mail(subject,
        #     message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    except Exception as e:
        print("error: ", e)
        return Response({'status': 'Error', 'message': 'Error al enviar la Constancia por correo.'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 'OK', 'message': 'Constancia enviada por correo correctamente.'},
                    status=status.HTTP_200_OK)


def check_status_of_evidence(activity_id):
    activity = Activity.objects.get(id=activity_id)
    if bool(activity.certificate_file) == False:
        evidences = Evidence.objects.filter(
            activity_id=activity_id, type_evidence__is_optional=False).values('evidence_status')
        for evidence in evidences:
            if evidence['evidence_status'] != 'OK':
                return False
    else:
        return False
    activity.activity_status = 'OK'
    activity.save()
    return True


@api_view(['POST'])
@permission_classes([AllowAny])
def pyjwt_generator(request):
    activity_id = request.data['activity_id']
    activity = Activity.objects.get(id=activity_id)
    presenters = activity.presenter.full_name_academic
    for co_presenter in activity.co_presenter.all():
        presenters += ', ' + co_presenter.full_name_academic
    key = 'Pq7e6ll$2^uo'
    try:
        encoded_jwt = jwt.encode(
            {
                "Nombre": activity.name,
                "Presenter": str(presenters),
                "Date activity": str(activity.date_activity),
                "Area knowledge": activity.get_area_knowledge_display(),
                "Type": str(activity.type)
            },
            key,
            algorithm="HS256"
        )
        print("encoded_jwt", encoded_jwt)
        decode_jwt = jwt.decode(encoded_jwt, key, algorithms="HS256")
        print("decode_jwt", decode_jwt)
    except Exception as e:
        print("error: ", e)
        return Response({'status': 'Error', 'message': 'Problema al crear el JWT'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'OK', 'message': encoded_jwt}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def pyjwt_verify_qr(request):
    key = 'Pq7e6ll$2^uo'
    try:
        decode_jwt = jwt.decode(request.data['data'], key, algorithms="HS256")
        print("decode_jwt", decode_jwt)
    except:
        return Response({'status': 'Error', 'message': 'Problema al verificar el QR'},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'OK', 'message': 'QR valido', 'data': decode_jwt}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_activity_evidence(request):
    edited_type_activity = request.data['edited_evidence']
    print(edited_type_activity)
    if not edited_type_activity == None:
        status, res_type_evidence = con.select(table="activity_typeactivity_type_evidence",
                                               where="typeactivity_id='" + str(edited_type_activity) + "'")
        activity_evidence = []
        print("EVIDENCIAS DE TIPO DE ACTIVIDAD")
        for i in res_type_evidence:
            activity_evidence.append(i[2])
            print(i)
        activities = []
        status, res_activity = con.select(table="activity_activity",
                                          where="type_id='" + str(edited_type_activity) + "'")
        for j in res_activity:
            # print(j)
            activities.append(str(j[0]))

        for i in activities:
            sobrantes = []
            faltantes = []
            status, res_activity_evidence = con.select(table="activity_evidence",
                                                       where="activity_id = '" + i + "'")
            temp = []
            time = []
            id = []
            print("EVIDENCIAS DE ACTIVIDAD")
            for j in res_activity_evidence:
                print(j)
                temp.append(j[4])
                time.append(j[5])
                id.append(j[0])
            if not temp == activity_evidence:
                # EVIDENCIAS DEL TIPO DE ACTIVIDAD
                first_set = set(activity_evidence)
                sec_set = set(temp)  # EVIDENCIAS DE LA ACTIVIDAD
                differences = (first_set - sec_set).union(sec_set - first_set)
                # CALCULAR EVIDENCIAS FALTANTES
                for k in first_set:
                    if k not in sec_set:
                        faltantes.append(k)
                # CALCULAR EVIDENCIAS SOBRANTES
                for k in temp:
                    if k not in activity_evidence:
                        sobrantes.append(k)
                # INSERT
                for g in range(len(faltantes)):
                    now = str(date.today())
                    status, msg = con.insert(table="activity_evidence",
                                             fields="activity_id, type_evidence_id, created, modified, evidence_status",
                                             values=[str(i), str(faltantes[g]), now, now, 'DUE'])
                for g in range(len(sobrantes)):
                    status, msg = con.delete(table="activity_evidence",
                                             where="id = " + str(id[g]) + "")

    return Response({'status': 'OK', 'message': 'Rows Updated'}, status=sts.HTTP_200_OK)

class mapper:
    id: str = ""
    created_by_id: str = ""
    presenter: str = ""
    presenter_id: str = ""
    edition: str = ""
    type_of_public: str = ""
    area_knowledge: str = ""
    name: str = ""

# ESTADISTICAS
@api_view(['POST'])
@permission_classes([AllowAny])
def estadisticas(requests):
    presenter = Presenter.objects.filter(is_active=True).only('id','gender')
    data = {
        "U":{
            "N":{},
            "CN":{},
            "C":{},
            "S":{}
        },
        "P":{
            "N": {},
            "CN": {},
            "C": {},
            "S": {}
        },
        "O":{
            "N": {},
            "CN": {},
            "C": {},
            "S": {}
        }
    }
    ACTIVITY_COUNT_BY_UNIT_TYPE = {
        "TOTAL":0,
        "U":0,
        "P":0,
        "O":0
    }
    ACTIVITY_COUNT_BY_REGION = {
        "TOTAL":0,
        "N":0,
        "CN":0,
        "C":0,
        "S":0
    }
    ACTIVITY_COUNT_BY_TYPE_ACTIVITY = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_BY_TYPE_ACTIVITY_U = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_BY_TYPE_ACTIVITY_P = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_BY_TYPE_ACTIVITY_O = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_U = {
        "TOTAL": 0,
        "N": 0,
        "CN": 0,
        "C": 0,
        "S": 0
    }
    ACTIVITY_COUNT_P = {
        "TOTAL": 0,
        "N": 0,
        "CN": 0,
        "C": 0,
        "S": 0
    }
    ACTIVITY_COUNT_O = {
        "TOTAL": 0,
        "N": 0,
        "CN": 0,
        "C": 0,
        "S": 0
    }
    ACTIVITY_COUNT_KNOWLEDGE_AREA = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_KNOWLEDGE_AREA_U = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_KNOWLEDGE_AREA_P = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_KNOWLEDGE_AREA_O = {
        "TOTAL":0
    }
    ACTIVITY_COUNT_TYPE_PUBLIC = {
        "TOTAL":0,
        "INT":0,
        "EXT":0
    }
    ACTIVITY_COUNT_TYPE_PUBLIC_U = {
        "TOTAL":0,
        "INT":0,
        "EXT":0
    }
    ACTIVITY_COUNT_TYPE_PUBLIC_P = {
        "TOTAL":0,
        "INT":0,
        "EXT":0
    }
    ACTIVITY_COUNT_TYPE_PUBLIC_O = {
        "TOTAL":0,
        "INT":0,
        "EXT":0
    }
    counter = 0
    counter_u = 0
    counter_p = 0
    counter_o = 0



    activity = (Activity.objects.filter(edition_id=requests.data['id_edition'])
                .filter(presenter__isnull=False).filter(modality__isnull=False)
                .filter(activity_status="OK").filter(Q(type_of_public="EXT")| Q(type_of_public="INT"))
                .only('created_by','presenter','edition','type__name','area_knowledge','type_of_public'))
    representative = Representative.objects.only('user_id','origin_organizational_unit','origin_university')

    for i in activity:
        counter += 1
        for j in representative.filter(Q(origin_university__isnull=False) & Q(user_id=i.created_by_id)):
            if i.created_by_id == j.user_id:
                type = ''
                if j.origin_university != None:
                    type = j.origin_university.type
                    ACTIVITY_COUNT_TYPE_PUBLIC[i.type_of_public] += 1
                    if i.area_knowledge not in ACTIVITY_COUNT_KNOWLEDGE_AREA:
                        ACTIVITY_COUNT_KNOWLEDGE_AREA[i.area_knowledge] = 1
                    else:
                        ACTIVITY_COUNT_KNOWLEDGE_AREA[i.area_knowledge] += 1
                    if i.type.name not in ACTIVITY_COUNT_BY_TYPE_ACTIVITY:
                        ACTIVITY_COUNT_BY_TYPE_ACTIVITY[i.type.name] = 1
                    else:
                        ACTIVITY_COUNT_BY_TYPE_ACTIVITY[i.type.name] += 1
                    ACTIVITY_COUNT_BY_REGION[j.origin_university.region.__str__()] += 1
                    if type == "U":
                        counter_u += 1
                        ACTIVITY_COUNT_TYPE_PUBLIC_U[i.type_of_public] += 1
                        if i.area_knowledge not in ACTIVITY_COUNT_KNOWLEDGE_AREA_U:
                            ACTIVITY_COUNT_KNOWLEDGE_AREA_U[i.area_knowledge] = 1
                        else:
                            ACTIVITY_COUNT_KNOWLEDGE_AREA_U[i.area_knowledge] += 1
                        if i.type.name not in ACTIVITY_COUNT_BY_TYPE_ACTIVITY_U:
                            ACTIVITY_COUNT_BY_TYPE_ACTIVITY_U[i.type.name] = 1
                        else:
                            ACTIVITY_COUNT_BY_TYPE_ACTIVITY_U[i.type.name] += 1
                        ACTIVITY_COUNT_U[j.origin_university.region.__str__()] += 1
                    if type == "P":
                        counter_p += 1
                        ACTIVITY_COUNT_TYPE_PUBLIC_P[i.type_of_public] += 1
                        if i.area_knowledge not in ACTIVITY_COUNT_KNOWLEDGE_AREA_P:
                            ACTIVITY_COUNT_KNOWLEDGE_AREA_P[i.area_knowledge] = 1
                        else:
                            ACTIVITY_COUNT_KNOWLEDGE_AREA_P[i.area_knowledge] += 1
                        if i.type.name not in ACTIVITY_COUNT_BY_TYPE_ACTIVITY_P:
                            ACTIVITY_COUNT_BY_TYPE_ACTIVITY_P[i.type.name] = 1
                        else:
                            ACTIVITY_COUNT_BY_TYPE_ACTIVITY_P[i.type.name] += 1
                        ACTIVITY_COUNT_P[j.origin_university.region.__str__()] += 1
                if j.origin_university.name not in data[type][j.origin_university.region.__str__()]:
                    data[type][j.origin_university.region.__str__()][j.origin_university.name.__str__()] = 0
                else:
                    data[type][j.origin_university.region.__str__()][j.origin_university.name.__str__()] += 1
                ACTIVITY_COUNT_BY_UNIT_TYPE[type] += 1
        for j in representative.filter(Q(origin_organizational_unit__isnull=False) & Q(user_id=i.created_by_id)):
            if i.created_by_id == j.user_id:
                counter_o += 1
                ACTIVITY_COUNT_TYPE_PUBLIC[i.type_of_public] += 1
                ACTIVITY_COUNT_TYPE_PUBLIC_O[i.type_of_public] += 1
                if i.type.name not in ACTIVITY_COUNT_BY_TYPE_ACTIVITY:
                    ACTIVITY_COUNT_BY_TYPE_ACTIVITY[i.type.name] = 1
                else:
                    ACTIVITY_COUNT_BY_TYPE_ACTIVITY[i.type.name] += 1

                if i.area_knowledge not in ACTIVITY_COUNT_KNOWLEDGE_AREA:
                    ACTIVITY_COUNT_KNOWLEDGE_AREA[i.area_knowledge] = 1
                else:
                    ACTIVITY_COUNT_KNOWLEDGE_AREA[i.area_knowledge] += 1
                if i.area_knowledge not in ACTIVITY_COUNT_KNOWLEDGE_AREA_O:
                    ACTIVITY_COUNT_KNOWLEDGE_AREA_O[i.area_knowledge] = 1
                else:
                    ACTIVITY_COUNT_KNOWLEDGE_AREA_O[i.area_knowledge] += 1
                if i.type.name not in ACTIVITY_COUNT_BY_TYPE_ACTIVITY_O:
                    ACTIVITY_COUNT_BY_TYPE_ACTIVITY_O[i.type.name] = 1
                else:
                    ACTIVITY_COUNT_BY_TYPE_ACTIVITY_O[i.type.name] += 1

                if j.origin_organizational_unit.name not in data["O"][j.origin_organizational_unit.region.__str__()]:
                    data["O"][j.origin_organizational_unit.region.__str__()][j.origin_organizational_unit.name.__str__()] = 0
                else:
                    data["O"][j.origin_organizational_unit.region.__str__()][j.origin_organizational_unit.name.__str__()] += 1
                ACTIVITY_COUNT_BY_UNIT_TYPE["O"] += 1
                ACTIVITY_COUNT_O[j.origin_organizational_unit.region.__str__()] += 1
                ACTIVITY_COUNT_BY_REGION[j.origin_organizational_unit.region.__str__()] += 1
    gender = [0, 0]  # HOMBRE, MUJER
    for i in activity:
        if i.presenter != None:
            for j in presenter:
                if i.presenter_id == j.id:
                    if j.gender == "H":
                        gender[0] += 1
                    if j.gender == "M":
                        gender[1] += 1
    total = sum(gender)
    if total > 0:
        gender_percent = [round((gender[0] * 100) / total, 2),
                      round((gender[1] * 100) / total, 2)]

    ACTIVITY_COUNT_BY_UNIT_TYPE["U"] = round(
        (ACTIVITY_COUNT_BY_UNIT_TYPE["U"] * 100) / len(activity)-1, 2)
    ACTIVITY_COUNT_BY_UNIT_TYPE["P"] = round(
        (ACTIVITY_COUNT_BY_UNIT_TYPE["P"] * 100) / len(activity)-1, 2)
    ACTIVITY_COUNT_BY_UNIT_TYPE["O"] = round(
        (ACTIVITY_COUNT_BY_UNIT_TYPE["O"] * 100) / len(activity)-1, 2)

    ACTIVITY_COUNT_BY_REGION["N"] = round(
        (ACTIVITY_COUNT_BY_REGION["N"] * 100) / len(activity)-1, 2)
    ACTIVITY_COUNT_BY_REGION["CN"] = round(
        (ACTIVITY_COUNT_BY_REGION["CN"] * 100) /len(activity)-1, 2)
    ACTIVITY_COUNT_BY_REGION["C"] = round(
        (ACTIVITY_COUNT_BY_REGION["C"] * 100) / len(activity)-1, 2)
    ACTIVITY_COUNT_BY_REGION["S"] = round(
        (ACTIVITY_COUNT_BY_REGION["S"] * 100) / len(activity)-1, 2)

    ACTIVITY_COUNT_U["N"] = round(
        (ACTIVITY_COUNT_U["N"] * 100) / counter_u, 2)
    ACTIVITY_COUNT_U["CN"] = round(
        (ACTIVITY_COUNT_U["CN"] * 100) /counter_u, 2)
    ACTIVITY_COUNT_U["C"] = round(
        (ACTIVITY_COUNT_U["C"] * 100) / counter_u, 2)
    ACTIVITY_COUNT_U["S"] = round(
        (ACTIVITY_COUNT_U["S"] * 100) / counter_u, 2)

    ACTIVITY_COUNT_P["N"] = round(
        (ACTIVITY_COUNT_P["N"] * 100) / counter_p, 2)
    ACTIVITY_COUNT_P["CN"] = round(
        (ACTIVITY_COUNT_P["CN"] * 100) /counter_p, 2)
    ACTIVITY_COUNT_P["C"] = round(
        (ACTIVITY_COUNT_P["C"] * 100) / counter_p, 2)
    ACTIVITY_COUNT_P["S"] = round(
        (ACTIVITY_COUNT_P["S"] * 100) / counter_p, 2)

    ACTIVITY_COUNT_O["N"] = round(
        (ACTIVITY_COUNT_O["N"] * 100) / counter_o, 2)
    ACTIVITY_COUNT_O["CN"] = round(
        (ACTIVITY_COUNT_O["CN"] * 100) /counter_o, 2)
    ACTIVITY_COUNT_O["C"] = round(
        (ACTIVITY_COUNT_O["C"] * 100) / counter_o, 2)
    ACTIVITY_COUNT_O["S"] = round(
        (ACTIVITY_COUNT_O["S"] * 100) / counter_o, 2)

    U = [[],[],[],[]]
    P = [[],[],[],[]]
    O = [[],[],[],[]]
    for i in data['U']:
        for j in data['U'][i]:
            x = list(data['U'].keys()).index(i)
            U[x].append([list(data['U'][i])[list(data['U'][i].keys()).index(j)],data['U'][i][j]])
    for i in data['P']:
        for j in data['P'][i]:
            x = list(data['P'].keys()).index(i)
            P[x].append([list(data['P'][i])[list(data['P'][i].keys()).index(j)],data['P'][i][j]])
    for i in data['O']:
        for j in data['O'][i]:
            x = list(data['O'].keys()).index(i)
            O[x].append([list(data['O'][i])[list(data['O'][i].keys()).index(j)],data['O'][i][j]])

    data = {"U": U, "P": P, "O": O}


    response = {
        "CANTIDAD_ACTIVIDADES_POR_UNIDAD":data,
        "CANTIDAD_ACTIVIDADES_SUPERIOR": ACTIVITY_COUNT_U,
        "CANTIDAD_ACTIVIDADES_MEDSUP": ACTIVITY_COUNT_P,
        "CANTIDAD_ACTIVIDADES_ORG": ACTIVITY_COUNT_O,
        "CANTIDAD_ACTIVIDADES_POR_GENERO": {
            "H": gender_percent[0],
            "M": gender_percent[1]
        },
        "CANTIDAD_ACTIVIDADES_TIPO_UNIDAD": ACTIVITY_COUNT_BY_UNIT_TYPE,
        "CANTIDAD_ACTIVIDADES_POR_REGION": ACTIVITY_COUNT_BY_REGION,
        "CANTIDAD_ACTIVIDADES_TIPO_ACTIVIDAD": ACTIVITY_COUNT_BY_TYPE_ACTIVITY,
        "CANTIDAD_ACTIVIDADES_TIPO_ACTIVIDAD_SUPERIOR": ACTIVITY_COUNT_BY_TYPE_ACTIVITY_U,
        "CANTIDAD_ACTIVIDADES_TIPO_ACTIVIDAD_MEDSUP": ACTIVITY_COUNT_BY_TYPE_ACTIVITY_P,
        "CANTIDAD_ACTIVIDADES_TIPO_ACTIVIDAD_ORG": ACTIVITY_COUNT_BY_TYPE_ACTIVITY_O,
        "CANTIDAD_ACTIVIDADES_AREA_CONOCIMIENTO":ACTIVITY_COUNT_KNOWLEDGE_AREA,
        "CANTIDAD_ACTIVIDADES_AREA_CONOCIMIENTO_U": ACTIVITY_COUNT_KNOWLEDGE_AREA_U,
        "CANTIDAD_ACTIVIDADES_AREA_CONOCIMIENTO_P": ACTIVITY_COUNT_KNOWLEDGE_AREA_P,
        "CANTIDAD_ACTIVIDADES_AREA_CONOCIMIENTO_O": ACTIVITY_COUNT_KNOWLEDGE_AREA_O,
        "CANTIDAD_ACTIVIDADES_PUBLICO_DIRIGIDO": ACTIVITY_COUNT_TYPE_PUBLIC,
        "CANTIDAD_ACTIVIDADES_PUBLICO_DIRIGIDO_U": ACTIVITY_COUNT_TYPE_PUBLIC_U,
        "CANTIDAD_ACTIVIDADES_PUBLICO_DIRIGIDO_P": ACTIVITY_COUNT_TYPE_PUBLIC_P,
        "CANTIDAD_ACTIVIDADES_PUBLICO_DIRIGIDO_O": ACTIVITY_COUNT_TYPE_PUBLIC_O,
    }

    cached_statistics = response

    return Response(response, status=sts.HTTP_200_OK)