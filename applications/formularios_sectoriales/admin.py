from django.contrib import admin
from .models import *


class Paso1Inline(admin.TabularInline):
    model = Paso1
    extra = 0


class MarcoJuridicoInLine(admin.TabularInline):
    model = MarcoJuridico
    extra = 0


class OrganigramaRegionalInLine(admin.TabularInline):
    model = OrganigramaRegional
    extra = 0


class Paso2Inline(admin.TabularInline):
    model = Paso2
    extra = 0


class Paso3Inline(admin.TabularInline):
    model = Paso3
    extra = 0


class Paso4Inline(admin.TabularInline):
    model = Paso4
    extra = 0


class EncabezadoPaso4InLine(admin.TabularInline):
    model = Paso4Encabezado
    extra = 0


class Paso5Inline(admin.TabularInline):
    model = Paso5
    extra = 0


class ObservacionesSubdereInline(admin.TabularInline):
    model = ObservacionesSubdereFormularioSectorial
    extra = 0


class CoberturaAnualInLine(admin.TabularInline):
    model = CoberturaAnual
    extra = 0


class OrganismosIntervinientesInLine(admin.TabularInline):
    model = OrganismosIntervinientes
    extra = 0


class UnidadesIntervinientesInLine(admin.TabularInline):
    model = UnidadesIntervinientes
    extra = 0


class EtapasEjercicioCompetenciaInLine(admin.TabularInline):
    model = EtapasEjercicioCompetencia
    extra = 0


class PlataformasySoftwaresInLine(admin.TabularInline):
    model = PlataformasySoftwares
    extra = 0


class FlujogramaCompetenciaInLine(admin.TabularInline):
    model = FlujogramaCompetencia
    extra = 0


class CostosDirectosInLine(admin.TabularInline):
    model = CostosDirectos
    extra = 0

class EvolucionGastoAsociadoInLine(admin.TabularInline):
    model = EvolucionGastoAsociado
    extra = 0


@admin.register(FormularioSectorial)
class FormularioSectorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'get_competencia_nombre', 'formulario_enviado')
    list_filter = ('formulario_enviado', 'competencia')
    search_fields = ('nombre', 'competencia__nombre')
    ordering = ('nombre',)
    raw_id_fields = ('competencia',)
    inlines = [
        Paso1Inline,
        MarcoJuridicoInLine,
        OrganigramaRegionalInLine,
        Paso2Inline,
        CoberturaAnualInLine,
        OrganismosIntervinientesInLine,
        UnidadesIntervinientesInLine,
        EtapasEjercicioCompetenciaInLine,
        PlataformasySoftwaresInLine,
        FlujogramaCompetenciaInLine,
        Paso3Inline,
        Paso4Inline,
        EncabezadoPaso4InLine,
        Paso5Inline,
        CostosDirectosInLine,
        ObservacionesSubdereInline,
        EvolucionGastoAsociadoInLine
    ]

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre
    get_competencia_nombre.admin_order_field = 'competencia__nombre'  # Permite ordenar por este campo
    get_competencia_nombre.short_description = 'Nombre de la Competencia'  # Texto que se mostrará en la cabecera de la columna

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Usa select_related para optimizar la consulta de base de datos
        return queryset.select_related('competencia')


@admin.register(Paso1)
class Paso1Admin(admin.ModelAdmin):
    list_display = ('nombre_paso', 'numero_paso', 'formulario_sectorial_display')
    search_fields = ('nombre_paso', 'numero_paso')

    def formulario_sectorial_display(self, obj):
        return obj.formulario_sectorial

    formulario_sectorial_display.short_description = 'Formulario Sectorial Asociado'


class SubtitulosAdmin(admin.ModelAdmin):
    list_display = ('id', 'subtitulo',)
    search_fields = ('subtitulo',)

class ItemSubtituloAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'subtitulo',)
    search_fields = ('item', 'subtitulo__subtitulo',)
    list_filter = ('subtitulo',)

admin.site.register(Subtitulos, SubtitulosAdmin)
admin.site.register(ItemSubtitulo, ItemSubtituloAdmin)
admin.site.register(Paso2)