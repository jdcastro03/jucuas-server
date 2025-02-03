from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.DeadlineViewSet.as_view({ 'get': 'list' })), #listado de fechas de la jornada universitaria
    path('create/', views.DeadlineViewSet.as_view({ 'post': 'create' })), #Creacion de fechas de la jornada universitaria
    path('<int:pk>/', views.DeadlineViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de de fechas de la jornada universitaria por id
    path('current/', views.current_deadline),
    path('upload_file/', views.upload_file)
]