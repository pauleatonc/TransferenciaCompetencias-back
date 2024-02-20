from django.contrib import admin
from .models import SectorGubernamental, Ministerio
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource


class SectorGubernamentalResource(ModelResource):
    class Meta:
        model = SectorGubernamental


class MinisterioResource(ModelResource):
    class Meta:
        model = Ministerio


@admin.register(SectorGubernamental)
class SectorGubernamentalAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SectorGubernamentalResource
    list_display = ('id', 'nombre', 'get_ministerio_nombre')
    search_fields = ('nombre', 'ministerio__nombre')

    def get_ministerio_nombre(self, obj):
        return obj.ministerio.nombre

    get_ministerio_nombre.short_description = 'Ministerio'


@admin.register(Ministerio)
class MinisterioAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = MinisterioResource
    list_display = ('id', 'nombre')