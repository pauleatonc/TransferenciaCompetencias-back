from django.urls import include, re_path


urlpatterns = [

    re_path('', include('applications.sectores_gubernamentales.api.v1.urls'))
]
