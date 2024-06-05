import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso5Encabezado,
    Paso5,
    IndicadorDesempeno
)


class Command(BaseCommand):
    help = 'Crea Paso5Encabezado, y Paso5 sectorial para todas las Competencias existentes'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                competencias = Competencia.objects.all()
                for competencia in competencias:
                    formularios_sectoriales = FormularioSectorial.objects.filter(competencia=competencia)

                    for formulario_sectorial in formularios_sectoriales:
                        # Crear Paso5Encabezado si no existe
                        Paso5Encabezado.objects.get_or_create(formulario_sectorial=formulario_sectorial)

                        # Verificar y crear Paso5 por cada región
                        paso_instances = Paso5.objects.filter(formulario_sectorial=formulario_sectorial)
                        if paso_instances.exists():
                            # Asignar la primera región a las instancias existentes
                            region_asignada = False
                            for paso in paso_instances:
                                if paso.region is None and not region_asignada:
                                    for region in competencia.regiones.all():
                                        paso.region = region
                                        paso.save()
                                        region_asignada = True
                                        break
                        # Crear las instancias faltantes
                        existing_regions = paso_instances.values_list('region', flat=True)
                        for region in competencia.regiones.all():
                            if region.id not in existing_regions:
                                Paso5.objects.create(formulario_sectorial=formulario_sectorial, region=region)

                    self.stdout.write(self.style.SUCCESS('Instancias creadas exitosamente para todas las competencias.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            sys.exit(1)