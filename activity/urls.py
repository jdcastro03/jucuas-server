from django.urls import path
from . import views

urlpatterns = [
    # Actividades
    path('list/', views.ActivityViewSet.as_view({ 'get': 'list' })), #listado de actividad
    path('create/', views.CreateActivityViewSet.as_view({ 'post': 'create' })), #Creacion de actividad
    path('<int:pk>/', views.ActivityViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de actividad por id
    path('partial/activity/<int:pk>/', views.PartialUpdateActivityViewSet.as_view()),
    path('partial/pdf/<int:pk>/', views.PartialUpdateSavePDFActivityViewSet.as_view()),
    path('list/presenter/', views.ActivityByPresenterViewSet.as_view({ 'get': 'list' })),
    path('list/representer/', views.ActivityByRepresenterViewSet.as_view({ 'get': 'list' })),
    path('list/region/', views.ActivityByRegionViewSet.as_view({ 'get': 'list' })),
    path('list/activity_constansy/', views.ActivityConstansy),
    path('filteredlisttable/', views.get_filteredlisttable),
    path('statistics/', views.estadisticas),

    # Evidencias
    path('evidence/list/', views.EvidenceViewSet.as_view({ 'get': 'list' })), #listado de evidencia
    path('evidence/create/', views.EvidenceViewSet.as_view({ 'post': 'create' })), #Creacion de evidencia
    path('evidence/<int:pk>/', views.PartialUpdateEvidenceViewSet.as_view()), #Obtencion/Eliminacion/Actualizacion de evidencia por id
    path('evidence/validate/<int:pk>/', views.PartialValidateEvidenceViewSet.as_view()),
    path('evidence/updateTables', views.update_activity_evidence),

    path('evidencesforactivity/<int:activity_id>/', views.EvidenceByActivityViewSet.as_view()),
    path('qr_generator/', views.qr_generator),
    path('pyjwt_generator/', views.pyjwt_generator),
    path('pyjwt_verify_qr/', views.pyjwt_verify_qr),
    path('send_certificate/', views.send_certificate),

    # Tipos de actividades
    path('type/activity/list/', views.TypeActivityViewSet.as_view({ 'get': 'list' })), #listado de Tipos de actividad
    path('type/activity/create/', views.TypeActivityViewSet.as_view({ 'post': 'create' })), #Creacion de Tipos de actividad
    path('type/activity/<int:pk>/', views.TypeActivityViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de Tipos de actividad por id

    # Tipos de evidencia
    path('type/evidence/list/', views.TypeEvidenceViewSet.as_view({ 'get': 'list' })), #listado de Tipos de evidencia
    path('type/evidence/create/', views.TypeEvidenceViewSet.as_view({ 'post': 'create' })), #Creacion de Tipos de evidencia
    path('type/evidence/<int:pk>/', views.TypeEvidenceViewSet.as_view({ 'get': 'retrieve', 'put':'partial_update', 'delete': 'destroy' })), #Obtencion/Eliminacion/Actualizacion de Tipos de evidencia por id

    # Actualizar Evidencias de actividad
    #path('updateActivityEvidence/', views.updateActivityEvidence)
]