from django.contrib import admin
from .models import *


class Paso1Inline(admin.TabularInline):
    model = Paso1
    extra = 0


class Paso2Inline(admin.TabularInline):
    model = Paso2
    can_delete = False
    max_num = 1
    extra = 1


class FlujogramaEjercicioInline(admin.TabularInline):
    model = FlujogramaEjercicioCompetencia
    extra = 0


@admin.register(FormularioGORE)
class FormularioSectorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'get_competencia_nombre', 'formulario_enviado')
    list_filter = ('formulario_enviado', 'competencia')
    search_fields = ('nombre', 'competencia__nombre')
    ordering = ('nombre',)
    raw_id_fields = ('competencia',)
    inlines = [
        Paso1Inline,
        Paso2Inline,
        FlujogramaEjercicioInline,
    ]

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre
    get_competencia_nombre.admin_order_field = 'competencia__nombre'  # Permite ordenar por este campo
    get_competencia_nombre.short_description = 'Nombre de la Competencia'  # Texto que se mostrará en la cabecera de la columna

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Usa select_related para optimizar la consulta de base de datos
        return queryset.select_related('competencia')
