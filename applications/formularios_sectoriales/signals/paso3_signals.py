from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_naive

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
        año_actual = competencia.fecha_inicio.year
        año_inicial = año_actual - 5

        for año in range(año_inicial, año_actual):
            CoberturaAnual.objects.get_or_create(
                formulario_sectorial=instance,
                anio=año
            )


@receiver(post_save, sender=Competencia)
def actualizar_coberturas_anuales(sender, instance, **kwargs):
    print("Signal para actualizar coberturas anuales activado.")  # Debug

    history = instance.historical.all()
    if history.count() > 1:
        # Usar el penúltimo registro histórico para comparar
        penultimo_historico = history[1]

        last_fecha_inicio = make_naive(penultimo_historico.instance.fecha_inicio).date()
        current_fecha_inicio = make_naive(instance.fecha_inicio).date()

        print(f"Penúltimo registro histórico encontrado. Fecha inicio anterior: {last_fecha_inicio}")  # Debug
        print(f"Fecha inicio actual: {current_fecha_inicio}")  # Debug

        if last_fecha_inicio != current_fecha_inicio:
            print(f"Cambio detectado en fecha de inicio. Nueva fecha: {current_fecha_inicio}")  # Debug
        print(f"Cambio detectado en fecha de inicio. Nueva fecha: {instance.fecha_inicio}")  # Debug
        año_actual = instance.fecha_inicio.year
        año_inicial = año_actual - 5

        formularios_sectoriales = FormularioSectorial.objects.filter(competencia=instance)
        print(f"Encontrados {formularios_sectoriales.count()} formularios sectoriales para actualizar.")  # Debug

        for formulario in formularios_sectoriales:
            # Eliminar todas las coberturas anuales existentes
            coberturas_eliminadas = CoberturaAnual.objects.filter(formulario_sectorial=formulario).delete()
            print(f"Eliminadas {coberturas_eliminadas[0]} coberturas anuales para el formulario {formulario.id}.")  # Debug

            # Crear nuevas coberturas anuales basadas en la nueva fecha de inicio
            for año in range(año_inicial, año_actual):
                CoberturaAnual.objects.create(
                    formulario_sectorial=formulario,
                    anio=año
                )
                print(f"Creada CoberturaAnual para el año {año} en el formulario {formulario.id}.")  # Debug
    else:
        print("No se detectaron cambios en la fecha de inicio.")  # Debug