from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .competenciasViewSet import CompetenciaViewSet
from .ambitoApiView import AmbitoViewSet
from .origenApiView import OrigenAPIView

router = DefaultRouter()
router.register(r'competencias', CompetenciaViewSet)
router.register(r'ambitos', AmbitoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('origenes/', OrigenAPIView.as_view(), name='origenes')
]
