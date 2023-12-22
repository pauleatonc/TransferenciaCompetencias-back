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

@receiver(post_save, sender=CostoAnio)
def actualizar_variacion_promedio(sender, instance, **kwargs):
    # Obtener la instancia de EvolucionGastoAsociado asociada
    evolucion_gasto = instance.evolucion_gasto

    # Obtener el rango de años
    costos_anio = CostoAnio.objects.filter(evolucion_gasto=evolucion_gasto).order_by('anio')
    if costos_anio:
        anio_mas_antiguo = costos_anio.first().anio
        anio_mas_reciente = costos_anio.last().anio

        # Obtener o crear la instancia de VariacionPromedio
        variacion, created = VariacionPromedio.objects.get_or_create(
            formulario_sectorial=evolucion_gasto.formulario_sectorial,
            subtitulo=evolucion_gasto.subtitulo
        )

        # Actualizar los campos gasto_n_5 y gasto_n_1
        variacion.gasto_n_5 = costos_anio.filter(anio=anio_mas_antiguo).first().costo
        variacion.gasto_n_1 = costos_anio.filter(anio=anio_mas_reciente).first().costo
        variacion.save()

        # Llamada al método calcular_variacion
        if variacion:
            variacion.calcular_variacion()