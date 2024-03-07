from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso2,
    CostosDirectosGore,
    CostosIndirectosGore,
    FluctuacionPresupuestaria,
    CostoAnioGore, ResumenCostosGore
)

from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    CostosDirectos as CostosDirectosSectorial,
    CostosIndirectos as CostosIndirectosSectorial,
)


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso1
        Paso2.objects.create(formulario_gore=instance)


def eliminar_instancias_gore_correspondientes(modelo_gore, instance):
    """
    Elimina instancias de costos de formulario GORE específico que corresponden
    a la instancia de costos de formulario sectorial eliminada. No elimina instancias
    que han sido creadas directamente en GORE (identificadas por tener el campo 'sector' como null).
    """
    sectorial_sector = instance.formulario_sectorial.sector
    item_subtitulo = instance.item_subtitulo
    competencia = instance.formulario_sectorial.competencia

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia)
    for formulario_gore in formularios_gore:
        # Filtra las instancias para eliminar, excluyendo aquellas con el campo 'sector' como null.
        modelo_gore.objects.filter(
            formulario_gore=formulario_gore,
            sector=sectorial_sector,
            item_subtitulo=item_subtitulo
        ).exclude(sector__isnull=True).delete()


def crear_o_actualizar_instancias_gore(modelo_gore, instance, created):

    formulario_sectorial = instance.formulario_sectorial
    competencia = formulario_sectorial.competencia
    sector = formulario_sectorial.sector

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia)
    for formulario_gore in formularios_gore:
        obj, created_gore = modelo_gore.objects.get_or_create(
            formulario_gore=formulario_gore,
            sector=sector,
            item_subtitulo=instance.item_subtitulo,
            defaults={'total_anual_sector': instance.total_anual}  # Ajusta según el modelo
        )
        if not created and not created_gore:
            obj.total_anual_sector = instance.total_anual  # Ajusta según el modelo
            obj.save()


@receiver(post_save, sender=CostosDirectosSectorial)
@receiver(post_save, sender=CostosIndirectosSectorial)
def crear_o_actualizar_costos_gore(sender, instance, created, **kwargs):
    if sender == CostosDirectosSectorial:
        crear_o_actualizar_instancias_gore(CostosDirectosGore, instance, created)
    else:
        crear_o_actualizar_instancias_gore(CostosIndirectosGore, instance, created)


@receiver(post_delete, sender=CostosDirectosSectorial)
@receiver(post_delete, sender=CostosIndirectosSectorial)
def eliminar_costos_gore_correspondiente(sender, instance, **kwargs):
    if sender == CostosDirectosSectorial:
        eliminar_instancias_gore_correspondientes(CostosDirectosGore, instance)
    else:
        eliminar_instancias_gore_correspondientes(CostosIndirectosGore, instance)


def actualizar_fluctuaciones_presupuestarias(formulario_gore_id):
    subtitulos_directos_ids = CostosDirectosGore.objects.filter(
        formulario_gore_id=formulario_gore_id
    ).values_list('item_subtitulo__subtitulo_id', flat=True).distinct()

    subtitulos_indirectos_ids = CostosIndirectosGore.objects.filter(
        formulario_gore_id=formulario_gore_id
    ).values_list('item_subtitulo__subtitulo_id', flat=True).distinct()

    subtitulos_unicos_ids = set(list(subtitulos_directos_ids) + list(subtitulos_indirectos_ids))

    for subtitulo_id in subtitulos_unicos_ids:
        # Asegura la existencia de EvolucionGastoAsociado
        FluctuacionPresupuestaria.objects.get_or_create(
            formulario_gore_id=formulario_gore_id,
            subtitulo_id=subtitulo_id,
        )

    # Eliminar instancias obsoletas de EvolucionGastoAsociado y VariacionPromedio
    FluctuacionPresupuestaria.objects.filter(formulario_gore_id=formulario_gore_id).exclude(
        subtitulo_id__in=subtitulos_unicos_ids).delete()


@receiver(post_save, sender=CostosDirectosGore)
@receiver(post_save, sender=CostosIndirectosGore)
@receiver(post_delete, sender=CostosDirectosGore)
@receiver(post_delete, sender=CostosIndirectosGore)
def actualizar_resumen_costos(sender, instance, **kwargs):
    # regenerar_resumen_costos(instance.formulario_gore_id)
    actualizar_fluctuaciones_presupuestarias(instance.formulario_gore_id)


@receiver(post_save, sender=FluctuacionPresupuestaria)
def handle_fluctuacion_presupuestaria_save(sender, instance, created, **kwargs):
    # Crear CostoAnioGore para FluctuacionPresupuestaria
    if created:
        competencia = instance.formulario_gore.competencia
        if competencia and competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            # Ajuste para crear instancias para los 5 años siguientes al año_actual
            año_final = año_actual + 5  # Esto incluirá desde el año siguiente al actual hasta 5 años después
            for año in range(año_actual + 1,
                             año_final + 1):  # +1 para empezar en el siguiente año y +1 para incluir el año final en el rango
                CostoAnioGore.objects.get_or_create(
                    evolucion_gasto=instance,
                    anio=año
                )


@receiver([post_save, post_delete], sender=CostosDirectosGore)
@receiver([post_save, post_delete], sender=CostosIndirectosGore)
def actualizar_resumen_costos(sender, instance, **kwargs):
    formulario_gore_id = instance.formulario_gore_id
    actualizar_resumen(formulario_gore_id)


def actualizar_resumen(formulario_gore_id):
    # Obtener o crear la instancia de ResumenCostosGore para el FormularioGORE correspondiente
    resumen, _ = ResumenCostosGore.objects.get_or_create(formulario_gore_id=formulario_gore_id)

    # Calcular sumatorias para costos directos
    directos_por_sector = \
        CostosDirectosGore.objects.filter(formulario_gore_id=formulario_gore_id).aggregate(Sum('total_anual_sector'))[
            'total_anual_sector__sum'] or 0
    directos_por_gore = \
        CostosDirectosGore.objects.filter(formulario_gore_id=formulario_gore_id).aggregate(Sum('total_anual_gore'))[
            'total_anual_gore__sum'] or 0

    # Calcular sumatorias para costos indirectos
    indirectos_por_sector = \
        CostosIndirectosGore.objects.filter(formulario_gore_id=formulario_gore_id).aggregate(Sum('total_anual_sector'))[
            'total_anual_sector__sum'] or 0
    indirectos_por_gore = \
        CostosIndirectosGore.objects.filter(formulario_gore_id=formulario_gore_id).aggregate(Sum('total_anual_gore'))[
            'total_anual_gore__sum'] or 0

    # Actualizar campos en ResumenCostosGore
    resumen.directos_por_sector = directos_por_sector
    resumen.directos_por_gore = directos_por_gore
    resumen.indirectos_por_sector = indirectos_por_sector
    resumen.indirectos_por_gore = indirectos_por_gore

    # Realizar cálculos de diferencias y totales
    resumen.diferencia_directos = directos_por_sector - directos_por_gore
    resumen.diferencia_indirectos = indirectos_por_sector - indirectos_por_gore
    resumen.costos_sector = directos_por_sector + indirectos_por_sector
    resumen.costos_gore = directos_por_gore + indirectos_por_gore
    resumen.diferencia_costos = resumen.costos_sector - resumen.costos_gore

    # Guardar el resumen actualizado
    resumen.save()
