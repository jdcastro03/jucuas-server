from datetime import datetime

from accounts.serializers import GroupsSerializer
from common.decorators.auth_decorator import group_required
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status

from .models import Deadline
from .serializers import DeadlineSerializer

# vista de fechas de la jornada universitaria
@method_decorator(group_required('admin','representative', 'reviewer'), name='dispatch')
class DeadlineViewSet(viewsets.ModelViewSet):
    serializer_class = DeadlineSerializer

    # lista de fechas de la jornada universitaria
    def get_queryset(self):
        return Deadline.objects.filter(status=True)

    # elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def current_deadline(request):
    print("DEADLINE")
    if request.data['deadline'] == 'upload_activities':
        if current_date_to_upload_activities():
            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        return Response({'status': 'Error', 'message': 'La fecha limite para subir actividades ya paso'},
                        status=status.HTTP_400_BAD_REQUEST)

    elif request.data['deadline'] == 'upload_evidences':
        if current_date_to_upload_evidences():
            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        return Response({'status': 'Error', 'message': 'La fecha limite para subir evidencias ya paso'},
                        status=status.HTTP_400_BAD_REQUEST)

    elif request.data['deadline'] == 'validate_evidences':
        if current_date_to_validate_evidences():
            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        return Response({'status': 'Error', 'message': 'La fecha limite para validar evidencias ya paso'},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'Error', 'message': 'Hubo un error con las fechas limite'},
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    id = request.data['id']
    file_name = request.data['file_name']
    file = request.data['file']
    data = {}
    evidence_obj = Deadline.objects.get(id=id)
    data['file'] = file
    data['file_name'] = file_name
    evidence_serializer = DeadlineSerializer(evidence_obj, data,  many=False)
    evidence_serializer.is_valid(raise_exception=True)
    evidence_serializer.save()
    return Response({'status':'OK', 'message' : 'Archivo subido'}, status=status.HTTP_200_OK)


def current_date_to_upload_activities():
    date = datetime.now().date()
    current = Deadline.objects.get(date_edition=date.year, status=1)
    if date < current.date_to_upload_activities:
        return True
    return False


def current_date_to_upload_evidences():
    date = datetime.now().date()
    current = Deadline.objects.get(date_edition=date.year, status=1)
    if date < current.date_to_upload_evidence:
        return True
    return False


def current_date_to_validate_evidences():
    date = datetime.now().date()
    current = Deadline.objects.last()
    if date < current.date_to_validate_evidence:
        return True
    return False