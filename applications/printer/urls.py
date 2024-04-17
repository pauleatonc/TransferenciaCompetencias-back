from django.urls import path
from . import views

urlpatterns = [
    path('preview/resumen/<int:competencia_id>/', views.resumen_competencia, name='competencia'),
    path('preview/formulario-sectorial/<int:formulario_sectorial_id>/', views.formulario_sectorial, name='formulario-sectorial'),
]
