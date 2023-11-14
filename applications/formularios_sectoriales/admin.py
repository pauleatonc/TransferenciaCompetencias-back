from django.contrib import admin
from .models import FormularioSectorial

@admin.register(FormularioSectorial)
class FormularioSectorialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'get_competencia_nombre', 'formulario_enviado')
    list_filter = ('formulario_enviado', 'etapa__competencia', 'usuario')
    search_fields = ('nombre', 'usuario__nombre_completo', 'etapa__competencia__nombre')
    ordering = ('nombre',)
    raw_id_fields = ('usuario', 'etapa')

    def get_competencia_nombre(self, obj):
        return obj.etapa.competencia.nombre
    get_competencia_nombre.admin_order_field = 'etapa__competencia__nombre'  # Permite ordenar por este campo
    get_competencia_nombre.short_description = 'Nombre de la Competencia'  # Texto que se mostrará en la cabecera de la columna

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Usa select_related para optimizar la consulta de base de datos
        return queryset.select_related('usuario', 'etapa', 'etapa__competencia')
