from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.formularios_sectoriales.models import (
    CostosDirectos,
    CostosIndirectos,
    ResumenCostosPorSubtitulo,
    Paso5,
    EvolucionGastoAsociado,
    VariacionPromedio,
    CostoAnio,
    FormularioSectorial
)
from django.utils import timezone


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso5
        Paso5.objects.create(formulario_sectorial=instance)


def gestionar_resumen_costos_por_subtitulo(instance):
    subtitulo_id = instance.item_subtitulo.subtitulo_id
    formulario_sectorial_id = instance.formulario_sectorial_id
    costos_directos = CostosDirectos.objects.filter(item_subtitulo__subtitulo_id=subtitulo_id, formulario_sectorial_id=formulario_sectorial_id).exists()
    costos_indirectos = CostosIndirectos.objects.filter(item_subtitulo__subtitulo_id=subtitulo_id, formulario_sectorial_id=formulario_sectorial_id).exists()

    # Verificar si existe alguna instancia de costos asociada al subtitulo
    if costos_directos or costos_indirectos:
        # Si existe al menos una instancia de costos, asegurar que exista un resumen
        ResumenCostosPorSubtitulo.objects.get_or_create(
            subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        )
    else:
        # Si no existen instancias de costos, eliminar el resumen si existe
        ResumenCostosPorSubtitulo.objects.filter(
            subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).delete()


@receiver(post_save, sender=CostosDirectos)
@receiver(post_save, sender=CostosIndirectos)
@receiver(post_delete, sender=CostosDirectos)
@receiver(post_delete, sender=CostosIndirectos)
def actualizar_resumen_costos_por_subtitulo(sender, instance, **kwargs):
    # Lógica para crear o eliminar el ResumenCostosPorSubtitulo
    gestionar_resumen_costos_por_subtitulo(instance)


@receiver(post_save, sender=EvolucionGastoAsociado)
def crear_costos_anios(sender, instance, created, **kwargs):
    if created:
        competencia = instance.formulario_sectorial.competencia
        # Verificar si fecha_inicio está definida
        if competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
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