from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ReviewerViewSet.as_view({ 'get': 'list' })), #listado de los revisadores
    #path('create/', views.ReviewerViewSet.as_view({ 'post': 'create' })), #Creacion de revisadores
    path('create/', views.register_reviewer),
    path('<int:pk>/', views.ReviewerViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de revisadores por id
]