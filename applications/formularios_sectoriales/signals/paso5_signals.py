from django.db.models import Sum
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
import time
from django.core.exceptions import ObjectDoesNotExist

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
    # Obtener todos los subtitulos únicos para este formulario sectorial que tienen un item_subtitulo
    subtitulos_directos = set(
        CostosDirectos.objects.filter(
            formulario_sectorial_id=formulario_sectorial_id,
            item_subtitulo__isnull=False  # Solo instancias con item_subtitulo
        ).values_list('item_subtitulo__subtitulo_id', flat=True))

    subtitulos_indirectos = set(
        CostosIndirectos.objects.filter(
            formulario_sectorial_id=formulario_sectorial_id,
            item_subtitulo__isnull=False  # Solo instancias con item_subtitulo
        ).values_list('item_subtitulo__subtitulo_id', flat=True))

    subtitulos_unicos = subtitulos_directos.union(subtitulos_indirectos)

    # Para cada subtitulo único, obtener o crear ResumenCostosPorSubtitulo y actualizar el total_anual
    for subtitulo_id in subtitulos_unicos:
        if subtitulo_id is None:
            continue  # Saltar si subtitulo_id es None

        total_directos = CostosDirectos.objects.filter(
            formulario_sectorial_id=formulario_sectorial_id,
            item_subtitulo__subtitulo_id=subtitulo_id
        ).aggregate(total=Sum('total_anual'))['total'] or 0

        total_indirectos = CostosIndirectos.objects.filter(
            formulario_sectorial_id=formulario_sectorial_id,
            item_subtitulo__subtitulo_id=subtitulo_id
        ).aggregate(total=Sum('total_anual'))['total'] or 0

        total_anual = total_directos + total_indirectos

        resumen_costos, created = ResumenCostosPorSubtitulo.objects.get_or_create(
            formulario_sectorial_id=formulario_sectorial_id,
            subtitulo_id=subtitulo_id,
            defaults={'total_anual': total_anual}
        )
        if not created:
            resumen_costos.total_anual = total_anual  # Actualizar el total_anual
            resumen_costos.save()

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
                    variaciones[f'variacion_gasto_n_{5 - i}'] = variacion

                VariacionPromedio.objects.update_or_create(
                    formulario_sectorial_id=formulario_sectorial_id,
                    subtitulo_id=subtitulo_id,
                    defaults=variaciones
                )


def actualizar_evolucion_y_variacion(formulario_sectorial_id):
    # Obtiene IDs de subtitulos a partir de CostosDirectos y CostosIndirectos con item_subtitulo no nulo
    subtitulos_directos_ids = CostosDirectos.objects.filter(
        formulario_sectorial_id=formulario_sectorial_id, item_subtitulo__isnull=False
    ).values_list('item_subtitulo__subtitulo_id', flat=True).distinct()

    subtitulos_indirectos_ids = CostosIndirectos.objects.filter(
        formulario_sectorial_id=formulario_sectorial_id, item_subtitulo__isnull=False
    ).values_list('item_subtitulo__subtitulo_id', flat=True).distinct()

    # Combina y elimina duplicados para obtener todos los IDs de subtitulo únicos
    subtitulos_unicos_ids = set(subtitulos_directos_ids) | set(subtitulos_indirectos_ids)

    for subtitulo_id in subtitulos_unicos_ids:
        if subtitulo_id is not None:  # Asegura que el subtitulo_id no sea nulo
            # Asegura la existencia de EvolucionGastoAsociado solo para subtitulos válidos
            EvolucionGastoAsociado.objects.get_or_create(
                formulario_sectorial_id=formulario_sectorial_id,
                subtitulo_id=subtitulo_id,
            )

            # Asegura la existencia de VariacionPromedio (sin calcular la variación aquí) solo para subtitulos válidos
            VariacionPromedio.objects.get_or_create(
                formulario_sectorial_id=formulario_sectorial_id,
                subtitulo_id=subtitulo_id,
            )

    # Ahora llama a la función para calcular y actualizar la variación promedio para los subtitulos válidos
    calcular_y_actualizar_variacion(formulario_sectorial_id)

    # Eliminar instancias obsoletas de EvolucionGastoAsociado y VariacionPromedio que no corresponden a subtitulos válidos
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
            variaciones[f'variacion_gasto_n_{5 - i}'] = variacion

        evolucion_gasto = EvolucionGastoAsociado.objects.get(id=evolucion_gasto_id)
        VariacionPromedio.objects.update_or_create(
            formulario_sectorial_id=evolucion_gasto.formulario_sectorial_id,
            subtitulo_id=evolucion_gasto.subtitulo_id,
            defaults=variaciones
        )


def get_item_subtitulo(item):
    return ItemSubtitulo.objects.get(item=item)


def get_calidad_juridica(calidad):
    return CalidadJuridica.objects.get(calidad_juridica=calidad)


def calcular_total_por_item(modelo, paso5_instance, item_subtitulo):
    return sum((item.total_anual or 0) for item in modelo.objects.filter(
        formulario_sectorial=paso5_instance.formulario_sectorial,
        item_subtitulo=item_subtitulo
    ))


def calcular_costos_por_justificar(paso5_instance, campos):
    """
    Calcula los costos por justificar y actualiza la instancia de Paso5.

    :param paso5_instance: La instancia de Paso5 que se está actualizando.
    :param campos: Diccionario con la configuración de los campos a calcular.
    """
    for campo_total, campo_justificado, campo_por_justificar in campos:
        total = getattr(paso5_instance, campo_total) or 0
        justificado = getattr(paso5_instance, campo_justificado) or 0
        por_justificar = total - justificado
        setattr(paso5_instance, campo_por_justificar, por_justificar)


def calcular_total_por_calidad(modelo, paso5_instance, calidad_juridica):
    if modelo == PersonalDirecto:
        campo_suma = 'renta_bruta'
    elif modelo == PersonalIndirecto:
        campo_suma = 'total_rentas'
    else:
        return 0

    return sum((getattr(personal, campo_suma) or 0) for personal in modelo.objects.filter(
        formulario_sectorial=paso5_instance.formulario_sectorial,
        calidad_juridica=calidad_juridica
    ))



items_y_campos_directos = {
    "01 - Personal de Planta": "sub21_total_personal_planta",
    "02 - Personal de Contrata": "sub21_total_personal_contrata",
    "03 - Otras Remuneraciones": "sub21_total_otras_remuneraciones",
    "04 - Otros Gastos en Personal": "sub21_total_gastos_en_personal",
}

calidades_y_campos_directos = {
    "Planta": "sub21_personal_planta_justificado",
    "Contrata": "sub21_personal_contrata_justificado",
    "Honorario a suma alzada": "sub21_otras_remuneraciones_justificado",
}

campos_directos = [
    ('sub21_total_personal_planta', 'sub21_personal_planta_justificado', 'sub21_personal_planta_justificar'),
    ('sub21_total_personal_contrata', 'sub21_personal_contrata_justificado', 'sub21_personal_contrata_justificar'),
    ('sub21_total_otras_remuneraciones', 'sub21_otras_remuneraciones_justificado',
     'sub21_otras_remuneraciones_justificar'),
    ('sub21_total_gastos_en_personal', 'sub21_gastos_en_personal_justificado',
     'sub21_gastos_en_personal_justificar'),
]

items_y_campos_indirectos = {
    "01 - Personal de Planta": "sub21b_total_personal_planta",
    "02 - Personal de Contrata": "sub21b_total_personal_contrata",
    "03 - Otras Remuneraciones": "sub21b_total_otras_remuneraciones",
    "04 - Otros Gastos en Personal": "sub21b_total_gastos_en_personal",
}

calidades_y_campos_indirectos = {
    "Planta": "sub21b_personal_planta_justificado",
    "Contrata": "sub21b_personal_contrata_justificado",
    "Honorario a suma alzada": "sub21b_otras_remuneraciones_justificado",
}

campos_indirectos = [
    ('sub21b_total_personal_planta', 'sub21b_personal_planta_justificado', 'sub21b_personal_planta_justificar'),
    ('sub21b_total_personal_contrata', 'sub21b_personal_contrata_justificado', 'sub21b_personal_contrata_justificar'),
    ('sub21b_total_otras_remuneraciones', 'sub21b_otras_remuneraciones_justificado',
     'sub21b_otras_remuneraciones_justificar'),
    ('sub21b_total_gastos_en_personal', 'sub21b_gastos_en_personal_justificado',
     'sub21b_gastos_en_personal_justificar'),
]


def actualizar_campos_paso5(sender, instance, modelo_costos, modelo_personal, items_y_campos, calidades_y_campos,
                            campos_costos_justificar, tipo_modelo, **kwargs):
    if isinstance(instance, Paso5):
        return

    try:
        paso5_instance = Paso5.objects.get(formulario_sectorial=instance.formulario_sectorial)
        total_especifico = 0

        # Calcular totales por item
        for item, campo in items_y_campos.items():
            item_subtitulo = get_item_subtitulo(item)
            total = calcular_total_por_item(modelo_costos, paso5_instance, item_subtitulo)
            setattr(paso5_instance, campo, total)

        # Calcular totales por calidad
        for calidad, campo in calidades_y_campos.items():
            calidad_juridica = get_calidad_juridica(calidad)
            total = calcular_total_por_calidad(modelo_personal, paso5_instance, calidad_juridica)
            setattr(paso5_instance, campo, total)
            total_especifico += total

        # Calcular el total general de todas las calidades
        if tipo_modelo == 'indirecto':
            total_general = sum(
                (personal.total_rentas or 0) for personal in PersonalIndirecto.objects.filter(
                    formulario_sectorial=paso5_instance.formulario_sectorial
                )
            )
        elif tipo_modelo == 'directo':
            total_general = sum(
                (personal.renta_bruta or 0) for personal in PersonalDirecto.objects.filter(
                    formulario_sectorial=paso5_instance.formulario_sectorial
                )
            )

        # Calcular el total de "otras calidades"
        total_otras_calidades = total_general - total_especifico
        if tipo_modelo == 'indirecto':
            paso5_instance.sub21b_gastos_en_personal_justificado = total_otras_calidades
        elif tipo_modelo == 'directo':
            paso5_instance.sub21_gastos_en_personal_justificado = total_otras_calidades
            pass

        # Calcular costos por justificar usando el argumento `campos_costos_justificar`
        calcular_costos_por_justificar(paso5_instance, campos_costos_justificar)

        paso5_instance.save()

    except Paso5.DoesNotExist:
        return


@receiver([post_save, post_delete], sender=CostosDirectos)
@receiver([post_save, post_delete], sender=PersonalDirecto)
def handler_directo(sender, instance, **kwargs):
    actualizar_campos_paso5(
        sender=sender,
        instance=instance,
        modelo_costos=CostosDirectos,
        modelo_personal=PersonalDirecto,
        items_y_campos=items_y_campos_directos,
        calidades_y_campos=calidades_y_campos_directos,
        campos_costos_justificar=campos_directos,
        tipo_modelo='directo',  # Especificar el tipo de modelo
        **kwargs
    )


@receiver([post_save, post_delete], sender=CostosIndirectos)
@receiver([post_save, post_delete], sender=PersonalIndirecto)
def handler_indirecto(sender, instance, **kwargs):
    actualizar_campos_paso5(
        sender=sender,
        instance=instance,
        modelo_costos=CostosIndirectos,
        modelo_personal=PersonalIndirecto,
        items_y_campos=items_y_campos_indirectos,
        calidades_y_campos=calidades_y_campos_indirectos,
        campos_costos_justificar=campos_indirectos,
        tipo_modelo='indirecto',  # Especificar el tipo de modelo
        **kwargs
    )


# Mapeo entre ItemSubtitulo y CalidadJuridica
relacion_item_calidad = {
    "01 - Personal de Planta": "Planta",
    "02 - Personal de Contrata": "Contrata",
    "03 - Otras Remuneraciones": "Honorario a suma alzada",
    "04 - Otros Gastos en Personal": ["Honorario asimilado a grado", "Comisión de servicio", "Otro"],
}


def actualizar_instancias_personal(modelo_costos, modelo_personal, instance, created=False):
    """
    Actualiza o elimina las instancias de Personal (Directo o Indirecto) basándose en el estado del item_subtitulo
    seleccionado en el modelo de costos. Específicamente, maneja la creación de instancias excluyendo el caso
    "04 - Otros Gastos en Personal" y elimina instancias asociadas a este ítem si ya no existen costos vinculados.
    """
    # Manejar la creación o actualización de costos
    if instance.item_subtitulo:
        item_subtitulo_texto = instance.item_subtitulo.item
        calidades = relacion_item_calidad.get(item_subtitulo_texto, [])

        if item_subtitulo_texto == "04 - Otros Gastos en Personal" and not created:
            # Si estamos actualizando y es el caso especial "04 - Otros Gastos en Personal",
            # verifica si se deben eliminar instancias de personal asociadas
            if not modelo_costos.objects.filter(item_subtitulo=instance.item_subtitulo).exists():
                # No hay más costos asociados a este ítem, eliminar todas las instancias de personal relacionadas
                personal_asociado = modelo_personal.objects.filter(
                    formulario_sectorial=instance.formulario_sectorial,
                    calidad_juridica__in=[CalidadJuridica.objects.get(calidad_juridica=calidad) for calidad in calidades]
                )
                personal_asociado.delete()
            return  # Finaliza la ejecución para este caso

        if not isinstance(calidades, list):
            calidades = [calidades]

        for calidad in calidades:
            calidad_juridica_obj, _ = CalidadJuridica.objects.get_or_create(calidad_juridica=calidad)
            # Solo crea la instancia de personal si aún no existe y no es el caso especial "04 - Otros Gastos en Personal"
            if not modelo_personal.objects.filter(formulario_sectorial=instance.formulario_sectorial,
                                                  calidad_juridica=calidad_juridica_obj).exists():
                modelo_personal.objects.create(
                    formulario_sectorial=instance.formulario_sectorial,
                    calidad_juridica=calidad_juridica_obj
                )
    else:
        # Manejar la eliminación de costos o la ausencia de item_subtitulo
        personal_a_eliminar = modelo_personal.objects.filter(formulario_sectorial=instance.formulario_sectorial)
        for personal in personal_a_eliminar:
            if not modelo_costos.objects.filter(formulario_sectorial=instance.formulario_sectorial,
                                                item_subtitulo__isnull=False).exclude(id=instance.id).exists():
                personal.delete()


@receiver(post_save, sender=CostosDirectos)
@receiver(post_delete, sender=CostosDirectos)
def actualizar_personal_directo(sender, instance, **kwargs):
    actualizar_instancias_personal(CostosDirectos, PersonalDirecto, instance)


@receiver(post_save, sender=CostosIndirectos)
@receiver(post_delete, sender=CostosIndirectos)
def actualizar_personal_indirecto(sender, instance, **kwargs):
    actualizar_instancias_personal(CostosIndirectos, PersonalIndirecto, instance)
