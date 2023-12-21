from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.base import models
from applications.formularios_sectoriales.models import (
    CostosDirectos,
    CostosIndirectos,
    ResumenCostosPorSubtitulo,
    Paso5, EvolucionGastoAsociado, VariacionPromedio, CostoAnio, FormularioSectorial
)
from django.utils import timezone


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso5
        Paso5.objects.create(formulario_sectorial=instance)


def actualizar_resumenes_y_evoluciones(instance, modelo_costos):
    """
    Actualiza los resúmenes y evoluciones comunes después de eliminar un costo.
    """
    # Actualizar el total de costos en Paso5
    modelo_costos.actualizar_resumen_costos(instance)

    # Actualizar el total anual en ResumenCostosPorSubtitulo
    ResumenCostosPorSubtitulo.actualizar_total_anual(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)

    # Actualizar EvolucionGastoAsociado
    EvolucionGastoAsociado.actualizar_evolucion_por_subtitulo(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)

    # Si es CostosIndirectos, actualizar VariacionPromedio
    if modelo_costos == CostosIndirectos:
        VariacionPromedio.actualizar_variacion_por_subtitulo(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)


@receiver(post_delete, sender=CostosDirectos)
def post_delete_costos_directos(sender, instance, **kwargs):
    actualizar_resumenes_y_evoluciones(instance, CostosDirectos)


@receiver(post_delete, sender=CostosIndirectos)
def post_delete_costos_indirectos(sender, instance, **kwargs):
    actualizar_resumenes_y_evoluciones(instance, CostosIndirectos)


@receiver(post_delete, sender=ResumenCostosPorSubtitulo)
def post_delete_resumen_costos(sender, instance, **kwargs):
    ResumenCostosPorSubtitulo.actualizar_resumen_costos(instance)


@receiver(post_save, sender=EvolucionGastoAsociado)
def crear_costos_anios(sender, instance, created, **kwargs):
    if created:
        año_actual = timezone.now().year
        año_inicial = año_actual - 5

        for año in range(año_inicial, año_actual):
            CostoAnio.objects.get_or_create(
                evolucion_gasto=instance,
                anio=año
            )