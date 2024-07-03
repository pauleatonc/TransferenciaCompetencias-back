from django.urls import path, include, re_path

from applications.formularios_sectoriales.api.v1.FormularioSectorialViewSet import descargar_antecedente

app_name = 'formularios_sectoriales_app'

urlpatterns = [

    re_path('', include('applications.formularios_sectoriales.api.v1.routers')),
    path('descargar-antecedente/<int:pk>/', descargar_antecedente, name='descargar-antecedente'),

]