from django.urls import path
from . import views

urlpatterns = [
    path('preview/resumen/<int:competencia_id>/', views.resumen_competencia, name='competencia'),
    path('preview/formulario-sectorial_paso1/<int:formulario_sectorial_id>/', views.formulario_sectorial_paso1, name='formulario-sectorial_paso1'),
    path('preview/formulario-sectorial_paso2/<int:formulario_sectorial_id>/', views.formulario_sectorial_paso2, name='formulario-sectorial_paso2'),
    path('download/complete-document/<int:competencia_id>/', views.download_complete_document, name='complete-document'),
]
