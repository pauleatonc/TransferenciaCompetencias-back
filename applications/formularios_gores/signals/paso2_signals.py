from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso2,
    CostosDirectosGore,
    CostosIndirectosGore,
    FluctuacionPresupuestaria,
    CostoAnioGore,
    ResumenCostosGore,
    Paso3
)

from applications.formularios_sectoriales.models import (
    CostosDirectos as CostosDirectosSectorial,
    CostosIndirectos as CostosIndirectosSectorial,
    Subtitulos,
)


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso2
        Paso2.objects.create(formulario_gore=instance)


def eliminar_instancias_gore_correspondientes(modelo_gore, instance):
    """
    Elimina instancias GORE que corresponden a la instancia de costos sectoriales eliminada.
    """
    modelo_gore.objects.filter(id_sectorial=instance.id).delete()


def crear_o_actualizar_instancias_gore(modelo_gore, instance, created):
    subtitulo_texto = instance.subtitulo.subtitulo
    formulario_sectorial = instance.formulario_sectorial
    competencia = formulario_sectorial.competencia
    sector = formulario_sectorial.sector
    region = instance.region

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia, region=region)
    for formulario_gore in formularios_gore:
        try:
            # Busca la instancia GORE basada en el campo `id_sectorial`
            obj = modelo_gore.objects.get(
                formulario_gore=formulario_gore,
                id_sectorial=instance.id
            )
        except modelo_gore.DoesNotExist:
            # Si no existe, crea una nueva instancia vinculada con el ID sectorial
            obj = modelo_gore(
                formulario_gore=formulario_gore,
                sector=sector,
                subtitulo=instance.subtitulo,
                item_subtitulo=instance.item_subtitulo,
                total_anual_sector=instance.total_anual,
                descripcion=instance.descripcion if subtitulo_texto == 'Sub. 21' else '',
                id_sectorial=instance.id  # Copia el ID de la instancia sectorial
            )
            obj.save()
            continue

        # Actualiza los campos en el objeto GORE
        changed = False

        if obj.item_subtitulo != instance.item_subtitulo:
            obj.subtitulo = instance.subtitulo
            obj.item_subtitulo = instance.item_subtitulo
            obj.total_anual_gore = None  # Blanquear cuando cambia el item_subtitulo
            obj.es_transitorio = None    # Blanquear cuando cambia el item_subtitulo
            obj.descripcion = '' if subtitulo_texto != 'Sub. 21' else instance.descripcion  # Asegura que la descripción se blanquee o actualice según el subtítulo
            changed = True

        if obj.sector != sector:
            obj.sector = sector
            changed = True

        if obj.total_anual_sector != instance.total_anual:
            obj.total_anual_sector = instance.total_anual
            changed = True

        if subtitulo_texto == 'Sub. 21' and obj.descripcion != instance.descripcion:
            obj.descripcion = instance.descripcion
            changed = True

        # Guarda los cambios en la instancia GORE solo si hubo modificaciones
        if changed:
            obj.save()


@receiver(post_save, sender=CostosDirectosSectorial)
@receiver(post_save, sender=CostosIndirectosSectorial)
def crear_o_actualizar_costos_gore(sender, instance, created, **kwargs):
    if instance.item_subtitulo:
        if sender == CostosDirectosSectorial:
            crear_o_actualizar_instancias_gore(CostosDirectosGore, instance, created)
        else:
            crear_o_actualizar_instancias_gore(CostosIndirectosGore, instance, created)


@receiver(post_delete, sender=CostosDirectosSectorial)
@receiver(post_delete, sender=CostosIndirectosSectorial)
def eliminar_costos_gore_correspondiente(sender, instance, **kwargs):
    if instance.item_subtitulo:
        if sender == CostosDirectosSectorial:
            eliminar_instancias_gore_correspondientes(CostosDirectosGore, instance)
        else:
            eliminar_instancias_gore_correspondientes(CostosIndirectosGore, instance)


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


def actualizar_subtitulo_21_informados_gore(formulario_gore):
    sub_21, _ = Subtitulos.objects.get_or_create(subtitulo="Sub. 21")

    suma_costos_directos = CostosDirectosGore.objects.filter(
        formulario_gore=formulario_gore,
        sector__isnull=True,
        subtitulo=sub_21
    ).aggregate(suma_total_anual_gore=Sum('total_anual_gore'))['suma_total_anual_gore'] or 0

    suma_costos_indirectos = CostosIndirectosGore.objects.filter(
        formulario_gore=formulario_gore,
        sector__isnull=True,
        subtitulo=sub_21
    ).aggregate(suma_total_anual_gore=Sum('total_anual_gore'))['suma_total_anual_gore'] or 0

    # Actualiza el campo en Paso3
    paso3_instance = Paso3.objects.get(formulario_gore=formulario_gore)
    paso3_instance.subtitulo_21_informados_gore = suma_costos_directos + suma_costos_indirectos
    paso3_instance.save()


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


@receiver([post_save, post_delete], sender=CostosDirectosGore)
@receiver([post_save, post_delete], sender=CostosIndirectosGore)
def actualizar_resumen_costos(sender, instance, **kwargs):
    formulario_gore_id = instance.formulario_gore_id
    actualizar_resumen(formulario_gore_id)
    actualizar_subtitulo_21_informados_gore(instance.formulario_gore)
    actualizar_fluctuaciones_presupuestarias(formulario_gore_id)
