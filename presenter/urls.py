from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.PresenterViewSet.as_view({ 'get': 'list' })), #listado de los presentadores
    #path('create/', views.PresenterViewSet.as_view({ 'post': 'create' })), #Creacion de presentadores
    path('create/', views.register_presenter),
    path('<int:pk>/', views.PresenterViewSet.as_view({'get': 'retrieve', 'put': 'partial_update', 'delete': 'destroy'})), #Obtencion/Eliminacion/Actualizacion de presentadores por id
    path('verify/', views.verify_exist),
    path('current/', views.PresenterProfile.as_view(), name='presenters'),

    path('update_gender/', views.update_gender),
    path('update_name/', views.update_name),
    path('update_phone/', views.update_phone),
    path('update_email/', views.update_email),

  
    path('<int:pk>/', views.PresenterViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de presentadores por id
    path('verify/', views.verify_exist),
    path('filteredlist/', views.get_filteredlist),
    path('filteredlisttable/', views.get_filteredlisttable),
    path('get_copresenter/', views.get_copresenter)
]

