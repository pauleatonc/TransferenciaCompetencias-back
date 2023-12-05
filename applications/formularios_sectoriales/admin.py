from django.contrib import admin
from .models import FormularioSectorial, Paso1

class Paso1Inline(admin.TabularInline):
    model = Paso1
    extra = 0

@admin.register(FormularioSectorial)
class FormularioSectorialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_competencia_nombre', 'formulario_enviado', 'get_paso1_info')
    list_filter = ('formulario_enviado', 'competencia')
    search_fields = ('nombre', 'competencia__nombre')
    ordering = ('nombre',)
    raw_id_fields = ('competencia',)

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre
    get_competencia_nombre.admin_order_field = 'competencia__nombre'  # Permite ordenar por este campo
    get_competencia_nombre.short_description = 'Nombre de la Competencia'  # Texto que se mostrará en la cabecera de la columna

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Usa select_related para optimizar la consulta de base de datos
        return queryset.select_related('competencia')

    def get_paso1_info(self, obj):
        paso1 = obj.pasos.first()  # Ajusta según la relación real
        if paso1:
            # Aquí puedes personalizar lo que deseas mostrar de Paso1
            return f"{paso1.forma_juridica_organismo}, {paso1.mision_institucional}"
        return "Información no disponible"

    get_paso1_info.short_description = 'Información de Paso 1'
