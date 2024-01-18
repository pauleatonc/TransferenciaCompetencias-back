from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .etapasViewSet import (
    Etapa1ViewSet,
    Etapa2ViewSet,
    Etapa3ViewSet,
    Etapa4ViewSet,
    Etapa5ViewSet,
)

router = DefaultRouter()
router.register(r'etapa1', Etapa1ViewSet)
router.register(r'etapa2', Etapa2ViewSet)
router.register(r'etapa3', Etapa3ViewSet)
router.register(r'etapa4', Etapa4ViewSet)
router.register(r'etapa5', Etapa5ViewSet)


urlpatterns = [
    path('', include(router.urls))
]
