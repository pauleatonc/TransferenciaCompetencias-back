from django.urls import path, include, re_path

app_name = 'formularios_gores_app'

urlpatterns = [

    re_path('', include('applications.formularios_gores.api.v1.routers')),

]