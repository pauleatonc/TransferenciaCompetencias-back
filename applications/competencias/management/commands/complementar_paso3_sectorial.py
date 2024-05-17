import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, Paso3Encabezado, Paso3, CoberturaAnual


class Command(BaseCommand):
    help = 'Crea Paso3Encabezado, Paso3 y CoberturaAnual para todas las Competencias existentes'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                competencias = Competencia.objects.all()
                for competencia in competencias:
                    formularios_sectoriales = FormularioSectorial.objects.filter(competencia=competencia)

                    for formulario_sectorial in formularios_sectoriales:
                        # Crear Paso3Encabezado si no existe
                        Paso3Encabezado.objects.get_or_create(formulario_sectorial=formulario_sectorial)

                        # Verificar y crear Paso3 por cada región
                        paso3_instances = Paso3.objects.filter(formulario_sectorial=formulario_sectorial)
                        if paso3_instances.exists():
                            # Asignar la primera región a las instancias existentes
                            region_asignada = False
                            for paso in paso3_instances:
                                if paso.region is None and not region_asignada:
                                    for region in competencia.regiones.all():
                                        paso.region = region
                                        paso.save()
                                        region_asignada = True
                                        break
                        # Crear las instancias faltantes
                        existing_regions = paso3_instances.values_list('region', flat=True)
                        for region in competencia.regiones.all():
                            if region.id not in existing_regions:
                                Paso3.objects.create(formulario_sectorial=formulario_sectorial, region=region)

                        # Verificar y crear CoberturaAnual por cada región y cada año
                        if competencia.fecha_inicio:
                            año_actual = competencia.fecha_inicio.year
                            año_inicial = año_actual - 5

                            cobertura_instances = CoberturaAnual.objects.filter(
                                formulario_sectorial=formulario_sectorial)
                            if cobertura_instances.exists():
                                # Asignar la primera región a las instancias existentes
                                region_asignada = False
                                for cobertura in cobertura_instances:
                                    if cobertura.region is None and not region_asignada:
                                        for region in competencia.regiones.all():
                                            cobertura.region = region
                                            cobertura.save()
                                            region_asignada = True
                                            break
                            # Crear las instancias faltantes
                            for region in competencia.regiones.all():
                                for año in range(año_inicial, año_actual):
                                    existing_cobertura = CoberturaAnual.objects.filter(
                                        formulario_sectorial=formulario_sectorial,
                                        anio=año,
                                        region=region
                                    ).first()
                                    if not existing_cobertura:
                                        CoberturaAnual.objects.create(
                                            formulario_sectorial=formulario_sectorial,
                                            anio=año,
                                            region=region
                                        )
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"Advertencia: competencia.fecha_inicio no está definida para la competencia {competencia.id}."))
                self.stdout.write(self.style.SUCCESS('Instancias creadas exitosamente para todas las competencias.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            sys.exit(1)
