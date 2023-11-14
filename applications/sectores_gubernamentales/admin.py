from django.contrib import admin
from .models import SectorGubernamental
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource


class SectorGubernamentalResource(ModelResource):
    class Meta:
        model = SectorGubernamental


@admin.register(SectorGubernamental)
class RegionAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SectorGubernamentalResource