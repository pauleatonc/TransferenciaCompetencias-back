from django.contrib import admin
from .models import Region, Comuna
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource


class RegionResource(ModelResource):
    class Meta:
        model = Region


class ComunaResource(ModelResource):
    class Meta:
        model = Comuna


@admin.register(Region)
class RegionAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = RegionResource


@admin.register(Comuna)
class ComunaAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ComunaResource