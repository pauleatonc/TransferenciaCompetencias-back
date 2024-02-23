from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from applications.formularios_sectoriales.models import (
    CostosDirectos,
    CostosIndirectos,
    ResumenCostosPorSubtitulo,
    Paso5,
    EvolucionGastoAsociado,
    VariacionPromedio,
    CostoAnio,
    FormularioSectorial,
    PersonalDirecto,
    PersonalIndirecto, Subtitulos, ItemSubtitulo, CalidadJuridica
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
            costos = list(CostoAnio.objects.filter(evolucion_gasto=evolucion_gasto).order_by('anio'))
            if len(costos) > 1:  # Asegurarse de que hay al menos dos costos para calcular variaciones
                gasto_n_1 = costos[-1].costo if costos[-1] and costos[-1].costo is not None else 0
                variaciones = {}

                # Calcular variaciones desde el primero hasta el penúltimo costo
                for i in range(len(costos) - 1):
                    costo_actual = costos[i].costo if costos[i] and costos[i].costo is not None else 0
                    variacion = costo_actual - gasto_n_1
                    variaciones[f'variacion_gasto_n_{5-i}'] = variacion

                VariacionPromedio.objects.update_or_create(
                    formulario_sectorial_id=formulario_sectorial_id,
                    subtitulo_id=subtitulo_id,
                    defaults=variaciones
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
        )

        # Asegura la existencia de VariacionPromedio (sin calcular la variación aquí)
        VariacionPromedio.objects.get_or_create(
            formulario_sectorial_id=formulario_sectorial_id,
            subtitulo_id=subtitulo_id,
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
def handle_evolucion_gasto_asociado_save(sender, instance, created, **kwargs):
    # Crear CostoAnio para nuevos EvolucionGastoAsociado
    if created:
        competencia = instance.formulario_sectorial.competencia
        if competencia and competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            año_inicial = año_actual - 5
            for año in range(año_inicial, año_actual):
                CostoAnio.objects.get_or_create(
                    evolucion_gasto=instance,
                    anio=año
                )


@receiver(post_save, sender=CostoAnio)
def handle_costo_anio_save(sender, instance, **kwargs):
    # Llamar a la función para calcular y actualizar la variación después de cada guardado
    # pero solo después de que la transacción actual se haya confirmado.
    def calcular_y_actualizar_wrapper():
        calcular_y_actualizar_variacion_para_costo_anio(instance.evolucion_gasto_id)

    transaction.on_commit(calcular_y_actualizar_wrapper)


def calcular_y_actualizar_variacion_para_costo_anio(evolucion_gasto_id):
    costos = list(CostoAnio.objects.filter(evolucion_gasto_id=evolucion_gasto_id).order_by('anio'))
    if len(costos) > 1:  # Asegurarse de que hay al menos dos costos para calcular variaciones
        gasto_n_1 = costos[-1].costo if costos[-1].costo is not None else 0
        variaciones = {}

        # Calcular variaciones desde el primero hasta el penúltimo costo
        for i in range(len(costos) - 1):
            costo_actual = costos[i].costo if costos[i].costo is not None else 0
            variacion = costo_actual - gasto_n_1
            variaciones[f'variacion_gasto_n_{5-i}'] = variacion

        evolucion_gasto = EvolucionGastoAsociado.objects.get(id=evolucion_gasto_id)
        VariacionPromedio.objects.update_or_create(
            formulario_sectorial_id=evolucion_gasto.formulario_sectorial_id,
            subtitulo_id=evolucion_gasto.subtitulo_id,
            defaults=variaciones
        )


@receiver([post_save, post_delete], sender=CostosDirectos)
@receiver([post_save, post_delete], sender=CostosIndirectos)
@receiver([post_save, post_delete], sender=PersonalDirecto)
@receiver([post_save, post_delete], sender=PersonalIndirecto)
def actualizar_campos_paso5(sender, instance, **kwargs):
    """
    Actualiza los campos en Paso5 cada vez que se guarden o eliminen instancias
    de los modelos relacionados.
    """
    # Asegurarse de que no estamos actualizando desde una instancia de Paso5
    if isinstance(instance, Paso5):
        return

    # Obtén la instancia de Paso5 relacionada
    paso5_instance = Paso5.objects.get(formulario_sectorial=instance.formulario_sectorial)

    """ Cálculos para sumar Subtítulo 21 en Costos Directos e indirectos"""
    personal_de_planta_item = ItemSubtitulo.objects.get(item="01 - Personal de Planta")
    personal_de_contrata_item = ItemSubtitulo.objects.get(item="02 - Personal de Contrata")

    # Calcula 'sub21_total_personal_planta'
    total_personal_planta = sum(
        item.total_anual for item in CostosDirectos.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            item_subtitulo=personal_de_planta_item
        )
    ) + sum(
        item.total_anual for item in CostosIndirectos.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            item_subtitulo=personal_de_planta_item
        )
    )
    paso5_instance.sub21_total_personal_planta = total_personal_planta

    # Calcula 'sub21_total_personal_contrata'
    total_personal_contrata = sum(
        item.total_anual for item in CostosDirectos.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            item_subtitulo=personal_de_contrata_item
        )
    ) + sum(
        item.total_anual for item in CostosIndirectos.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            item_subtitulo=personal_de_contrata_item
        )
    )
    paso5_instance.sub21_total_personal_contrata = total_personal_contrata

    # Calcula 'sub21_total_resto'
    sub_21 = Subtitulos.objects.get(subtitulo='Sub. 21')

    total_sub_21 = sum(
        item.total_anual for item in CostosDirectos.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            item_subtitulo__subtitulo=sub_21
        )
    ) + sum(
        item.total_anual for item in CostosIndirectos.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            item_subtitulo__subtitulo=sub_21
        )
    )
    # Resta los ítems de 'Personal de Planta' y 'Personal de Contrata'
    total_personal_planta_contrata = paso5_instance.sub21_total_personal_planta + paso5_instance.sub21_total_personal_contrata
    paso5_instance.sub21_total_resto = total_sub_21 - total_personal_planta_contrata

    """ Calcula los subtotales de Personal Directo e Indirecto por calidad jurídica"""
    personal_de_planta = CalidadJuridica.objects.get(calidad_juridica="Planta")
    personal_a_contrata = CalidadJuridica.objects.get(calidad_juridica="Contrata")

    # Calcula 'sub21_personal_planta_justificado'
    personal_justificado = sum(
        (personal.renta_bruta or 0) for personal in PersonalDirecto.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            calidad_juridica=personal_de_planta
        )
    ) + sum(
        (personal.renta_bruta or 0) for personal in PersonalIndirecto.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            calidad_juridica=personal_de_planta
        )
    )
    paso5_instance.sub21_personal_planta_justificado = personal_justificado

    # Calcula 'sub21_personal_contrata_justificado'
    personal_contrata_justificado = sum(
        (personal.renta_bruta or 0) for personal in PersonalDirecto.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            calidad_juridica=personal_a_contrata
        )
    ) + sum(
        (personal.renta_bruta or 0) for personal in PersonalIndirecto.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial,
            calidad_juridica=personal_a_contrata
        )
    )
    paso5_instance.sub21_personal_contrata_justificado = personal_contrata_justificado

    # Calcula 'sub21_resto_justificado'
    total_renta_bruta = sum(
        (personal.renta_bruta or 0) for personal in PersonalDirecto.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial
        )
    ) + sum(
        (personal.renta_bruta or 0) for personal in PersonalIndirecto.objects.filter(
            formulario_sectorial=paso5_instance.formulario_sectorial
        )
    )
    # Resta la renta bruta de 'Planta' y 'Contrata'
    total_renta_planta_contrata = paso5_instance.sub21_personal_planta_justificado + paso5_instance.sub21_personal_contrata_justificado
    paso5_instance.sub21_resto_justificado = total_renta_bruta - total_renta_planta_contrata

    """ Calcula los costos por justificar en cada caso: Planta, Contrata, resto de calidades juridicas"""
    # Calcula 'sub21_personal_planta_justificar'
    paso5_instance.sub21_personal_planta_justificar = (
            paso5_instance.sub21_total_personal_planta - paso5_instance.sub21_personal_planta_justificado
    )

    # Calcula 'sub21_personal_contrata_justificar'
    paso5_instance.sub21_personal_contrata_justificar = (
        paso5_instance.sub21_total_personal_contrata - paso5_instance.sub21_personal_contrata_justificado
    )

    # Calcula 'sub21_resto_justificar'
    paso5_instance.sub21_resto_justificar = (
            paso5_instance.sub21_total_resto - paso5_instance.sub21_resto_justificado
    )

    # Guarda la instancia de Paso5
    paso5_instance.save()