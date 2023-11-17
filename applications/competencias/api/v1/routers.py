from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .competenciasViewSet import CompetenciaViewSet

router = DefaultRouter()
router.register(r'competencias', CompetenciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
