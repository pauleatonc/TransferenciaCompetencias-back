from django.urls import path, include, re_path

app_name = 'formularios_sectoriales_app'

urlpatterns = [

    re_path('', include('applications.formularios_sectoriales.api.v1.routers')),
]