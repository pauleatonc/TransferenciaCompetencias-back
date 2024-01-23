from django.core.management.base import BaseCommand
from importlib import import_module


class Command(BaseCommand):
    help = 'Populate models from an Excel file'

    def handle(self, *args, **kwargs):
        populate_models_from_excel = import_module(
            "applications.sectores_gubernamentales.migrations.0004_asignar_valores_desde_excel").populate_models_from_excel()
        self.stdout.write(self.style.SUCCESS('Successfully populated models from Excel'))
