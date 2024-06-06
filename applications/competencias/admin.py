from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.conf import settings
from django.contrib.auth import get_user_model
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.formularios_gores.models import FormularioGORE

from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource



class Etapa1Inline(admin.TabularInline):  # O usa admin.StackedInline si prefieres ese estilo
    model = Etapa1
    extra = 0


class Etapa2Inline(admin.TabularInline):  # O usa admin.StackedInline si prefieres ese estilo
    model = Etapa2
    extra = 0


class Etapa3Inline(admin.TabularInline):  # O usa admin.StackedInline si prefieres ese estilo
    model = Etapa3
    extra = 0


class Etapa4Inline(admin.TabularInline):  # O usa admin.StackedInline si prefieres ese estilo
    model = Etapa4
    extra = 0


class Etapa5Inline(admin.TabularInline):  # O usa admin.StackedInline si prefieres ese estilo
    model = Etapa5
    extra = 0

class FormularioSectorialInline(admin.TabularInline):  # O puedes usar admin.StackedInline
    model = FormularioSectorial
    extra = 0
    fields = ('sector', 'nombre', 'formulario_enviado')

class FormularioGOREInline(admin.TabularInline):  # O puedes usar admin.StackedInline
    model = FormularioGORE
    extra = 0
    fields = ('region', 'nombre', 'formulario_enviado')


class CompetenciaResource(ModelResource):
    class Meta:
        model = Competencia

class CompetenciaAgrupadaInline(admin.TabularInline):
    model = CompetenciaAgrupada
    extra = 0

class Paso1InLine(admin.TabularInline):
    model = Paso1RevisionFinalSubdere
    extra = 0

class Paso2InLine(admin.TabularInline):
    model = Paso2RevisionFinalSubdere
    extra = 0


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin, ImportExportMixin):
    resource_class = CompetenciaResource
    list_display = ('id', 'nombre', 'ambito_competencia', 'origen', 'estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'sectores__nombre', 'regiones__nombre')
    list_filter = ('ambito_competencia', 'origen', 'estado', 'sectores', 'regiones')
    filter_horizontal = ('usuarios_subdere', 'usuarios_dipres', 'usuarios_sectoriales', 'usuarios_gore')
    fieldsets = (
        (None, {
            'fields': (
            'nombre', 'agrupada', 'creado_por', 'sectores', 'regiones', 'ambito_competencia', 'origen', 'fecha_inicio', 'fecha_fin',
            'formulario_final_enviado', 'plazo_formulario_sectorial', 'plazo_formulario_gore', 'oficio_origen')
        }),
        ('Usuarios', {
            'fields': ('usuarios_subdere', 'usuarios_dipres', 'usuarios_sectoriales', 'usuarios_gore')
        }),
    )
    inlines = [
        CompetenciaAgrupadaInline,
        Etapa1Inline,
        Etapa2Inline,
        Etapa3Inline,
        Etapa4Inline,
        Etapa5Inline,
        FormularioSectorialInline,
        FormularioGOREInline,
        Paso1InLine,
        Paso2InLine
    ]  # Añade el nuevo inline aquí

    def get_queryset(self, request):
        # Personaliza el queryset para optimizar consultas a la base de datos si es necesario
        return super().get_queryset(request)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Personaliza el campo formfield para restringir las opciones de ManyToMany basadas en cierta lógica
        if db_field.name in ["SUBDERE", "DIPRES", "Usuarios Sectoriales", "GORE"]:
            User = get_user_model()
            # Asume que los nombres de los grupos en el modelo Group son singulares (sin la 's' al final)
            kwargs["queryset"] = User.objects.filter(groups__name=db_field.name[:-1])
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Guarda el modelo estableciendo el campo creado_por al usuario que crea el objeto
        if not obj.pk:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # Lógica adicional después de guardar relaciones ManyToMany si es necesario
        super().save_related(request, form, formsets, change)

@admin.register(CompetenciaAgrupada)
class CompetenciaAgrupadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')