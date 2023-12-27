from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .competenciasViewSet import CompetenciaViewSet
from .ambitoApiView import AmbitoViewSet

router = DefaultRouter()
router.register(r'competencias', CompetenciaViewSet)
router.register(r'ambitos', AmbitoViewSet)

urlpatterns = [
    path('', include(router.urls))
]
