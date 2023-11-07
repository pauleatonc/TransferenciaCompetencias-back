from django.urls import path
from .views import RegionComunaView

urlpatterns = [
    path(
        'region-comuna/v1/',
        RegionComunaView.as_view(),
        name='region-comuna'
    ),
]