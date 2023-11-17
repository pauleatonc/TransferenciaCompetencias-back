from django.urls import path
from .views import RegionView

urlpatterns = [
    path(
        'region/v1/',
        RegionView.as_view(),
        name='region'
    ),
]