from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from common.decorators.auth_decorator import group_required
from django.utils.decorators import method_decorator

from .models import Reviewer
from .serializers import ReviewerSerializer

@api_view(['POST'])
@group_required('admin')
def register_reviewer(request):
    serializer = ReviewerSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# vista Revisadores
@method_decorator(group_required('admin') , name='dispatch')
class ReviewerViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewerSerializer

    #lista de los Revisadores
    def get_queryset(self):
        return Reviewer.objects.filter(status=True)
    
    #elimina la instancia recibida
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = False
        instance.save()