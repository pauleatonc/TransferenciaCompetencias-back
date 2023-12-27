from django.urls import path, include, re_path

app_name = 'etapas_app'

urlpatterns = [

    re_path('', include('applications.etapas.api.v1.routers')),

]