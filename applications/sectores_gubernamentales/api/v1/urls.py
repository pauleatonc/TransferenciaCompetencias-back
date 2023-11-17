from django.urls import path
from .views import SectorGubernamentalView

urlpatterns = [
    path(
        'sector-gubernamental/v1/',
        SectorGubernamentalView.as_view(),
        name='sector-gubernamenta'
    ),
]