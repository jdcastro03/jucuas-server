from django.urls import path
from . import views

urlpatterns = [
    # universidades
    path('university/list/', views.UniversityViewSet.as_view({ 'get': 'list' })), #listado de universidades
    path('university/create/', views.UniversityViewSet.as_view({ 'post': 'create' })), #Creacion de universidades
    path('university/<int:pk>/', views.UniversityViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de universidades por id
    path('university/table/', views.UniversityViewSet.as_view({ 'get': 'table' })), #listado de universidades
    #unidades organizacionales
    path('organizational-unit/list/', views.OrganizationalUnitViewSet.as_view({ 'get': 'list' })), #listado de Unidades Organizacionales
    path('organizational-unit/create/', views.OrganizationalUnitViewSet.as_view({ 'post': 'create' })), #Creacion de Unidades Organizacionales
    path('organizational-unit/<int:pk>/', views.OrganizationalUnitViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de Unidades Organizacionales por id
]