from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.formularios_sectoriales.models import FormularioSectorial, CoberturaAnual, Paso3, Paso3Encabezado


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso3Encabezado
        Paso3Encabezado.objects.create(formulario_sectorial=instance)

        competencia = instance.competencia
        # Crear instancia de Paso3 por cada región asociada a la competencia
        for region in competencia.regiones.all():
            Paso3.objects.create(formulario_sectorial=instance, region=region)


@receiver(post_save, sender=FormularioSectorial)
def crear_coberturas_anuales(sender, instance, created, **kwargs):
    if created:
        competencia = instance.competencia
        if competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            año_inicial = año_actual - 5

            # Crear instancias de CoberturaAnual por cada región asociada a la competencia
            for region in competencia.regiones.all():
                for año in range(año_inicial, año_actual):
                    CoberturaAnual.objects.get_or_create(
                        formulario_sectorial=instance,
                        anio=año,
                        region=region
                    )
        else:
            print("Advertencia: competencia.fecha_inicio no está definida.")
