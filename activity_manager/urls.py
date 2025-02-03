from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ActivityManagerViewSet.as_view({ 'get': 'list' })), #listado de los responsables de actividad
    path('create/', views.ActivityManagerViewSet.as_view({ 'post': 'create' })), #Creacion de responsables de actividad
    path('<int:pk>/', views.ActivityManagerViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de responsables de actividad por id
]