from django.urls import path, include, re_path

app_name = 'competencias_app'

urlpatterns = [

    re_path('', include('applications.competencias.api.v1.routers')),

]