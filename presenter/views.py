from django.db.models import Value
from accounts.models import User
from rest_framework import status, viewsets, generics
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.decorators.auth_decorator import group_required
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from representative.models import Representative
from reviewer.models import Reviewer
from university.models import University, OrganizationalUnit
from . import serializers
from .paginations import CustomPagination
from rest_framework.views import APIView
from .models import Presenter
from .serializers import PresenterSerializer, VerifySerializer
from accounts import views as cuenta
from django.db.models.functions import Concat

import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@group_required('admin', 'representative')
def register_presenter(request):
    curp = request.data.get('curp')
    email = request.data.get('email')
    phone = request.data.get('phone')
    if not (verify_create('curp', curp) or verify_create('email', email) or verify_create('phone', phone)):
        request.data['created_by'] = request.auth.user_id

        serializer = PresenterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": None}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "No se pudo crear el presentador. El correo, CURP o teléfono ya se encuentran registrados"}, status=status.HTTP_200_OK)

class PresenterProfile(APIView):
    permission_classes = (IsAuthenticated,)

# vista Presentadores
@method_decorator(group_required('admin', 'representative'), name='dispatch')
class PresenterViewSet(viewsets.ModelViewSet):
    serializer_class = PresenterSerializer
    pagination_class = CustomPagination
    
    #lista de los presentadores
    def get_queryset(self):
        return Presenter.objects.filter(status=True)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()
    # def update(self, request, *args, **kwargs):


def get(id):
    return  Presenter.objects.get(pk=id)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_gender(request):
    # Obtener presentador
    d=request.data;u=get(d['id'])
    print(d)
    # Cambiar genero y guardar objeto
    u.gender=d['gender'];u.save()
    return Response('1')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_name(request):
    d = request.data;u = get(d['id'])
    u.first_name=d['fn'];u.last_name=d['ln']
    u.save(); return Response('1')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_phone(request):
    d = request.data;u = get(d['id'])
    u.phone=d['phone']
    u.save(); return Response('1')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_email(request):
    # d: {id: presentador email: correo nuevo}
    # _u: usuario general
    # u: presentador

    d = request.data;u = get(d['id'])
    _u = User.objects.get(pk=u.user_id)
    u.email=d['email'];_u.email=d['email']
    _u.save();u.save()
    return Response('1')

@api_view(['POST'])
def get_filteredlist(request):
    filter = request.data.get('filter')
    queryset = Presenter.objects.annotate(search_name=Concat('first_name', Value(' '), 'last_name'))
    data = queryset.filter(search_name__icontains=filter, status=True)

    _json = []
    for i in data:
        _json.append({"id":i.id, "first_name": i.first_name, "last_name": i.last_name})
    return Response(_json, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_filteredlisttable(request):
    filter = request.data.get('filter')
    page = int(request.GET['p'])
    page_size = int(request.GET['page_size'])
    offset = page * page_size - page_size
    limit = offset + page_size
    data = []
    next = None
    previous = None
    queryset = Presenter.objects.annotate(search_name=Concat('first_name', Value(' '), 'last_name'))
    count = queryset.filter(search_name__icontains=filter, status=True).count()
    for p in queryset.filter(search_name__icontains=filter, status=True)[offset:limit]:
        data.append({"id": p.id, "first_name": p.first_name, "last_name": p.last_name, "is_active": p.status})
    if limit < count:
        next = f"presenters/filteredlisttable/?p={page + 1}&page_size={page_size}"
    if page > 1:
        previous = f"presenters/filteredlisttable/?p={page - 1}&page_size={page_size}"

    response = {
        "count": count,
        "next": next,
        "previous": previous,
        "results": data
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_copresenter(request):
    filter = request.data.get('id')
    data_first = Presenter.objects.filter(id=filter)
    _json = []
    for i in data_first:
        _json.append({"id":i.id, "first_name": i.first_name, "last_name": i.last_name})
    return Response(_json, status=status.HTTP_200_OK)

@api_view(['POST'])
@group_required('admin', 'representative')
def verify_exist(request):
    user = request.data.get('user')
    if str(user) == 'add':
        data = {request.data.get('type'): request.data.get('data')}
        if request.data.get('type') == 'username':
            if User.objects.filter(**data).exists():
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
        elif request.data.get('type') == 'email':
            if University.objects.filter(**data).exists() or OrganizationalUnit.objects.filter(
                    **data).exists() or Presenter.objects.filter(**data).exists() or Representative.objects.filter(
                    **data).exists() or Reviewer.objects.filter(**data).exists():
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
        elif request.data.get('type') == 'phone':
            if University.objects.filter(**data).exists() or OrganizationalUnit.objects.filter(
                    **data).exists() or Presenter.objects.filter(**data).exists():
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
        else:
            if Presenter.objects.filter(**data).exists():
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
    else:
        data = {request.data.get('type'): request.data.get('data')}
        if request.data.get('type') == 'username':
            data2 = {'user_name': request.data.get('data')}
            if (User.objects.filter(**data).exists()) and (not(
            Reviewer.objects.filter(**data2, id=user).exists() or
            Representative.objects.filter(**data2, id=user).exists())):
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
        elif request.data.get('type') == 'email':
            if (University.objects.filter(**data).exists() or OrganizationalUnit.objects.filter(
            **data).exists() or User.objects.filter(**data).exists()) and (not(University.objects.filter(**data, id=user).exists() or OrganizationalUnit.objects.filter(
            **data, id=user).exists() or Presenter.objects.filter(**data, id=user).exists() or
            Reviewer.objects.filter(**data, id=user).exists() or Representative.objects.filter(**data, id=user).exists())):
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
        elif request.data.get('type') == 'phone': #listo
            if (University.objects.filter(**data).exists() or OrganizationalUnit.objects.filter(
            **data).exists() or Presenter.objects.filter(**data).exists()) and (not(
                    Presenter.objects.filter(**data, id=user).exists()
            or University.objects.filter(**data, id=user).exists()
                    or OrganizationalUnit.objects.filter(**data, id=user).exists())):
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)
        else:
            if Presenter.objects.filter(**data).exists() and not Presenter.objects.filter(**data, id=user):
                return Response("1", status=status.HTTP_200_OK)
            else:
                return Response("0", status=status.HTTP_200_OK)

def verify_create(type, data):
    data = {type: data}
    if type == 'username':
        if User.objects.filter(**data).exists():
            return True
        else:
            return False
    elif type == 'email':
        if University.objects.filter(**data).exists() or OrganizationalUnit.objects.filter(
                **data).exists() or Presenter.objects.filter(**data).exists() or Representative.objects.filter(
                **data).exists() or Reviewer.objects.filter(**data).exists():
            return True
        else:
            return False
    elif type == 'phone':
        if University.objects.filter(**data).exists() or OrganizationalUnit.objects.filter(
                **data).exists() or Presenter.objects.filter(**data).exists():
            return True
        else:
            return False
    else:
        if Presenter.objects.filter(**data).exists():
            return True
        else:
            return False
