from django.db.models.signals import post_save
from django.dispatch import receiver

from simple_history.models import HistoricalRecords

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, CoberturaAnual, Paso3


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso3
        Paso3.objects.create(formulario_sectorial=instance)


@receiver(post_save, sender=FormularioSectorial)
def crear_coberturas_anuales(sender, instance, created, **kwargs):
    if created:
        competencia = instance.competencia
        # Verificar si fecha_inicio está definida
        if competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            año_inicial = año_actual - 5

            for año in range(año_inicial, año_actual):
                CoberturaAnual.objects.get_or_create(
                    formulario_sectorial=instance,
                    anio=año
                )
        else:
            print("Advertencia: competencia.fecha_inicio no está definida.")


@receiver(post_save, sender=Competencia)
def actualizar_coberturas_anuales(sender, instance, **kwargs):
    history = instance.historical.all()
    if history.count() > 1:
        # Usar el penúltimo registro histórico para comparar
        penultimo_historico = history[1]

        last_fecha_inicio = penultimo_historico.instance.fecha_inicio
        current_fecha_inicio = instance.fecha_inicio

        if last_fecha_inicio != current_fecha_inicio:
            año_actual = instance.fecha_inicio.year
            año_inicial = año_actual - 5

            formularios_sectoriales = FormularioSectorial.objects.filter(competencia=instance)

            for formulario in formularios_sectoriales:
                # Eliminar todas las coberturas anuales existentes
                CoberturaAnual.objects.filter(formulario_sectorial=formulario).delete()

                # Crear nuevas coberturas anuales basadas en la nueva fecha de inicio
                for año in range(año_inicial, año_actual):
                    CoberturaAnual.objects.create(
                        formulario_sectorial=formulario,
                        anio=año
                    )
