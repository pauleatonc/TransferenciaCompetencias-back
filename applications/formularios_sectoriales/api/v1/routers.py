from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .FormularioSectorialViewSet import FormularioSectorialViewSet

router = DefaultRouter()
router.register(r'formulario-sectorial', FormularioSectorialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
