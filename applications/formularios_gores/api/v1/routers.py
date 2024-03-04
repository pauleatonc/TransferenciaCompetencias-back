from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .FormularioGOREViewSet import FormularioGOREViewSet

router = DefaultRouter()
router.register(r'formulario-gore', FormularioGOREViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
