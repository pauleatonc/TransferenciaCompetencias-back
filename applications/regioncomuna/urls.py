from django.urls import include, re_path


urlpatterns = [

    re_path('', include('applications.regioncomuna.api.v1.urls'))
]
