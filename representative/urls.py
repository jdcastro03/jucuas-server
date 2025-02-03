from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.RepresentativeViewSet.as_view({ 'get': 'list' })), #listado de los representantes
    #path('create/', views.RepresentativeViewSet.as_view({ 'post': 'create' })), #Creacion de representantes
    path('create/', views.register_representative),
    path('<int:pk>/', views.RepresentativeViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de representantes por id
]