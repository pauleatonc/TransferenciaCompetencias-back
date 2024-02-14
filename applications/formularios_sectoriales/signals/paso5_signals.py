from django.db.models import Sum
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


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso5
        Paso5.objects.create(formulario_sectorial=instance)


def regenerar_resumen_costos(formulario_sectorial_id):
    # Obtener todos los subtitulos únicos para este formulario sectorial
    subtitulos_directos = set(
        CostosDirectos.objects.filter(formulario_sectorial_id=formulario_sectorial_id).values_list(
            'item_subtitulo__subtitulo_id', flat=True))
    subtitulos_indirectos = set(
        CostosIndirectos.objects.filter(formulario_sectorial_id=formulario_sectorial_id).values_list(
            'item_subtitulo__subtitulo_id', flat=True))

    subtitulos_unicos = subtitulos_directos.union(subtitulos_indirectos)

    # Obtener o crear ResumenCostosPorSubtitulo para cada subtitulo único y actualizar el total_anual
    for subtitulo_id in subtitulos_unicos:
        total_directos = CostosDirectos.objects.filter(formulario_sectorial_id=formulario_sectorial_id,
                                                       item_subtitulo__subtitulo_id=subtitulo_id).aggregate(
            total=Sum('total_anual'))['total'] or 0
        total_indirectos = CostosIndirectos.objects.filter(formulario_sectorial_id=formulario_sectorial_id,
                                                           item_subtitulo__subtitulo_id=subtitulo_id).aggregate(
            total=Sum('total_anual'))['total'] or 0
        total_anual = total_directos + total_indirectos

        resumen_costos, created = ResumenCostosPorSubtitulo.objects.get_or_create(
            formulario_sectorial_id=formulario_sectorial_id,
            subtitulo_id=subtitulo_id,
            defaults={'total_anual': total_anual}
        )
        if not created:
            # Si la instancia ya existía, actualizamos solo el total_anual
            ResumenCostosPorSubtitulo.objects.filter(id=resumen_costos.id).update(total_anual=total_anual)

    # Identificar y eliminar cualquier ResumenCostosPorSubtitulo obsoleto
    ResumenCostosPorSubtitulo.objects.filter(
        formulario_sectorial_id=formulario_sectorial_id
    ).exclude(
        subtitulo_id__in=subtitulos_unicos
    ).delete()


def calcular_y_actualizar_variacion(formulario_sectorial_id):
    subtitulos_ids = EvolucionGastoAsociado.objects.filter(
        formulario_sectorial_id=formulario_sectorial_id
    ).values_list('subtitulo_id', flat=True).distinct()

    for subtitulo_id in subtitulos_ids:
        evolucion_gasto = EvolucionGastoAsociado.objects.filter(
            formulario_sectorial_id=formulario_sectorial_id,
            subtitulo_id=subtitulo_id
        ).first()

        if evolucion_gasto:
            costos = CostoAnio.objects.filter(evolucion_gasto=evolucion_gasto).order_by('anio')
            if costos:
                gasto_n_5 = costos.first().costo if costos.first() and costos.first().costo is not None else 0
                gasto_n_1 = costos.last().costo if costos.last() and costos.last().costo is not None else 0
                variacion = gasto_n_1 - gasto_n_5

                VariacionPromedio.objects.update_or_create(
                    formulario_sectorial_id=formulario_sectorial_id,
                    subtitulo_id=subtitulo_id,
                    defaults={
                        'gasto_n_5': gasto_n_5,
                        'gasto_n_1': gasto_n_1,
                        'variacion': variacion,
                        'descripcion': ''
                    }
                )


def actualizar_evolucion_y_variacion(formulario_sectorial_id):
    subtitulos_directos_ids = CostosDirectos.objects.filter(
        formulario_sectorial_id=formulario_sectorial_id
    ).values_list('item_subtitulo__subtitulo_id', flat=True).distinct()

    subtitulos_indirectos_ids = CostosIndirectos.objects.filter(
        formulario_sectorial_id=formulario_sectorial_id
    ).values_list('item_subtitulo__subtitulo_id', flat=True).distinct()

    subtitulos_unicos_ids = set(list(subtitulos_directos_ids) + list(subtitulos_indirectos_ids))

    for subtitulo_id in subtitulos_unicos_ids:
        # Asegura la existencia de EvolucionGastoAsociado
        EvolucionGastoAsociado.objects.get_or_create(
            formulario_sectorial_id=formulario_sectorial_id,
            subtitulo_id=subtitulo_id,
            defaults={'descripcion': ''}
        )

        # Asegura la existencia de VariacionPromedio (sin calcular la variación aquí)
        VariacionPromedio.objects.get_or_create(
            formulario_sectorial_id=formulario_sectorial_id,
            subtitulo_id=subtitulo_id,
            defaults={'descripcion': ''}
        )

    # Ahora llama a la función para calcular y actualizar la variación promedio
    calcular_y_actualizar_variacion(formulario_sectorial_id)

    # Eliminar instancias obsoletas de EvolucionGastoAsociado y VariacionPromedio
    EvolucionGastoAsociado.objects.filter(formulario_sectorial_id=formulario_sectorial_id).exclude(
        subtitulo_id__in=subtitulos_unicos_ids).delete()
    VariacionPromedio.objects.filter(formulario_sectorial_id=formulario_sectorial_id).exclude(
        subtitulo_id__in=subtitulos_unicos_ids).delete()


@receiver(post_save, sender=CostosDirectos)
@receiver(post_save, sender=CostosIndirectos)
@receiver(post_delete, sender=CostosDirectos)
@receiver(post_delete, sender=CostosIndirectos)
def actualizar_resumen_costos(sender, instance, **kwargs):
    regenerar_resumen_costos(instance.formulario_sectorial_id)
    actualizar_evolucion_y_variacion(instance.formulario_sectorial_id)


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