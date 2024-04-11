from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static


# Swagger para documentación de la API
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


schema_view = get_schema_view(
   openapi.Info(
      title="Proyectos API",
      default_version='v1',
      description="Documentación de API de Proyectos de Banco de Proyectos",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

api_path_prefix = settings.API_PATH_PREFIX

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(api_path_prefix, include('applications.users.urls')),
    re_path(api_path_prefix, include('applications.regioncomuna.urls')),
    re_path(api_path_prefix, include('applications.sectores_gubernamentales.urls')),
    re_path(api_path_prefix, include('applications.competencias.urls')),
    re_path(api_path_prefix, include('applications.formularios_sectoriales.urls')),
    re_path(api_path_prefix, include('applications.formularios_gores.urls')),
    re_path(api_path_prefix, include('applications.etapas.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
