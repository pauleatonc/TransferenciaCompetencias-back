from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, CoberturaAnual, Paso3, Paso3Encabezado
from applications.regioncomuna.models import Region


@receiver(post_save, sender=FormularioSectorial)
def crear_encabezado_paso3(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso3Encabezado
        Paso3Encabezado.objects.create(formulario_sectorial=instance)

        # Obtener todas las regiones asociadas a la competencia del formulario
        competencia = instance.competencia
        if competencia:
            regiones = competencia.regiones.all()
            for region in regiones:
                # Crear instancias de Paso3 para cada región
                Paso3.objects.create(
                    formulario_sectorial=instance,
                    region=region
                )
                # Crear coberturas anuales
                if competencia.fecha_inicio:
                    año_actual = competencia.fecha_inicio.year
                    año_inicial = año_actual - 5
                    for año in range(año_inicial, año_actual):
                        CoberturaAnual.objects.create(
                            formulario_sectorial=instance,
                            anio=año,
                            region=region
                        )
        else:
            print("Advertencia: No hay competencia asociada al formulario sectorial.")


@receiver(m2m_changed, sender=Competencia.regiones.through)
def crear_instancias_relacionadas(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for formulario_sectorial in FormularioSectorial.objects.filter(competencia=instance):
            for region_pk in pk_set:
                region = Region.objects.get(pk=region_pk)
                # Crear instancias de Paso3
                Paso3.objects.get_or_create(
                    formulario_sectorial=formulario_sectorial,
                    region=region
                )
                # Crear coberturas anuales
                if instance.fecha_inicio:
                    año_actual = instance.fecha_inicio.year
                    año_inicial = año_actual - 5
                    for año in range(año_inicial, año_actual):
                        CoberturaAnual.objects.get_or_create(
                            formulario_sectorial=formulario_sectorial,
                            anio=año,
                            region=region
                        )
                else:
                    print("Advertencia: competencia.fecha_inicio no está definida.")

    elif action == 'post_remove':
        for formulario_sectorial in FormularioSectorial.objects.filter(competencia=instance):
            for region_pk in pk_set:
                Paso3.objects.filter(
                    formulario_sectorial=formulario_sectorial,
                    region_id=region_pk
                ).delete()
                CoberturaAnual.objects.filter(
                    formulario_sectorial=formulario_sectorial,
                    region_id=region_pk
                ).delete()
