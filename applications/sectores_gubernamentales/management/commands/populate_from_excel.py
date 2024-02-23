from django.core.management.base import BaseCommand
from importlib import import_module
from applications.formularios_sectoriales.models import Subtitulos, ItemSubtitulo


class Command(BaseCommand):
    help = 'Populate models from an Excel file'

    def handle(self, *args, **kwargs):
        populate_sectores_from_excel = import_module(
            "applications.sectores_gubernamentales.migrations.0004_asignar_valores_desde_excel").populate_sectores_from_excel()
        self.stdout.write(self.style.SUCCESS('Cargaste satisfactoriamente SectorGubernamental y Ministerio desde Excel'))

        populate_subtitulos_from_excel = import_module(
            "applications.formularios_sectoriales.migrations.0018_asignar_subtitulos_desde_excel").populate_subtitulos_e_items_from_excel()
        self.stdout.write(self.style.SUCCESS('Cargaste satisfactoriamente Subtitulos e Items desde Excel'))
