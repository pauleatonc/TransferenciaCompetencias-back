from django.db.models import Sum, Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import time

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso3,
    PersonalDirectoGORE,
    PersonalIndirectoGORE,
    RecursosComparados,
    SistemasInformaticos,
    RecursosFisicosInfraestructura,
    CostosDirectosGore,
    CostosIndirectosGore,
)

from applications.formularios_sectoriales.models import (
    PersonalDirecto,
    PersonalIndirecto,
    Subtitulos,
    ItemSubtitulo,
    CalidadJuridica
)

@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso3
        Paso3.objects.create(formulario_gore=instance)


@receiver(post_save, sender=PersonalDirecto)
@receiver(post_save, sender=PersonalIndirecto)
def crear_o_actualizar_personal_gore(sender, instance, created, **kwargs):
    # Inicializa campos_adicionales vacío para asegurar que siempre esté definido
    campos_adicionales = {}

    # Determina el modelo GORE basado en el tipo de modelo que disparó la señal
    if sender == PersonalDirecto:
        modelo_gore = PersonalDirectoGORE
    else:  # PersonalIndirecto
        modelo_gore = PersonalIndirectoGORE
        campos_adicionales = {
            'numero_personas': instance.numero_personas,
            'total_rentas': instance.total_rentas
        }

    formulario_sectorial = instance.formulario_sectorial
    competencia = formulario_sectorial.competencia
    sector = formulario_sectorial.sector

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia)
    for formulario_gore in formularios_gore:
        defaults = {
            'estamento': instance.estamento,
            'calidad_juridica': instance.calidad_juridica,
            'renta_bruta': instance.renta_bruta,
            'grado': instance.grado,
            'comision_servicio': True,
            **campos_adicionales  # Incorpora campos adicionales según el tipo de personal
        }
        obj, created_gore = modelo_gore.objects.get_or_create(
            formulario_gore=formulario_gore,
            id_sectorial=instance.id,  # Utiliza el ID sectorial para encontrar y actualizar la instancia correspondiente en GORE
            sector=sector,
            defaults=defaults
        )
        if not created_gore:
            for attr, value in defaults.items():
                setattr(obj, attr, value)
            obj.save()


@receiver(post_delete, sender=PersonalDirecto)
@receiver(post_delete, sender=PersonalIndirecto)
def eliminar_personal_gore_correspondiente(sender, instance, **kwargs):
    modelo_gore = PersonalDirectoGORE if sender == PersonalDirecto else PersonalIndirectoGORE

    # Utiliza el ID sectorial para encontrar y eliminar la instancia correspondiente en GORE
    modelo_gore.objects.filter(id_sectorial=instance.id).delete()


def get_item_subtitulo(item):
    return ItemSubtitulo.objects.get(item=item)


def get_calidad_juridica(calidad):
    return CalidadJuridica.objects.get(calidad_juridica=calidad)


def calcular_total_por_item(modelo, paso3_instance, item_subtitulo):
    return sum((item.total_anual_sector or 0) for item in modelo.objects.filter(
        formulario_gore=paso3_instance.formulario_gore,
        item_subtitulo=item_subtitulo
    ))


def calcular_costos_por_justificar(paso3_instance, campos):
    """
    Calcula los costos por justificar y actualiza la instancia de Paso3.

    :param paso3_instance: La instancia de Paso3 que se está actualizando.
    :param campos: Diccionario con la configuración de los campos a calcular.
    """
    for campo_total, campo_justificado, campo_por_justificar in campos:
        total = getattr(paso3_instance, campo_total) or 0
        justificado = getattr(paso3_instance, campo_justificado) or 0
        por_justificar = total - justificado
        setattr(paso3_instance, campo_por_justificar, por_justificar)


def calcular_total_por_calidad(modelo, paso3_instance, calidad_juridica):
    if modelo == PersonalDirecto:
        campo_suma = 'renta_bruta'
    elif modelo == PersonalIndirecto:
        campo_suma = 'total_rentas'
    else:
        return 0

    return sum((getattr(personal, campo_suma) or 0) for personal in modelo.objects.filter(
        formulario_gore=paso3_instance.formulario_gore,
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


def actualizar_campos_paso3(sender, instance, modelo_costos, modelo_personal, items_y_campos, calidades_y_campos,
                            campos_costos_justificar, tipo_modelo, **kwargs):
    if isinstance(instance, Paso3):
        return

    try:
        paso3_instance = Paso3.objects.get(formulario_gore=instance.formulario_gore)
        total_especifico = 0

        # Calcular totales por item
        for item, campo in items_y_campos.items():
            item_subtitulo = get_item_subtitulo(item)
            total = calcular_total_por_item(modelo_costos, paso3_instance, item_subtitulo)
            setattr(paso3_instance, campo, total)

        # Calcular totales por calidad
        for calidad, campo in calidades_y_campos.items():
            calidad_juridica = get_calidad_juridica(calidad)
            total = calcular_total_por_calidad(modelo_personal, paso3_instance, calidad_juridica)
            setattr(paso3_instance, campo, total)
            total_especifico += total

        # Calcular el total general de todas las calidades
        if tipo_modelo == 'indirecto':
            total_general = sum(
                (personal.total_rentas or 0) for personal in PersonalIndirectoGORE.objects.filter(
                    formulario_gore=paso3_instance.formulario_gore
                )
            )
        elif tipo_modelo == 'directo':
            total_general = sum(
                (personal.renta_bruta or 0) for personal in PersonalDirectoGORE.objects.filter(
                    formulario_gore=paso3_instance.formulario_gore
                )
            )

        # Calcular el total de "otras calidades"
        total_otras_calidades = total_general - total_especifico
        if tipo_modelo == 'indirecto':
            paso3_instance.sub21b_gastos_en_personal_justificado = total_otras_calidades
        elif tipo_modelo == 'directo':
            paso3_instance.sub21_gastos_en_personal_justificado = total_otras_calidades
            pass

        # Calcular costos por justificar usando el argumento `campos_costos_justificar`
        calcular_costos_por_justificar(paso3_instance, campos_costos_justificar)

        paso3_instance.save()

    except Paso3.DoesNotExist:
        return


@receiver([post_save, post_delete], sender=CostosDirectosGore)
@receiver([post_save, post_delete], sender=PersonalDirectoGORE)
def handler_directo(sender, instance, **kwargs):
    actualizar_campos_paso3(
        sender=sender,
        instance=instance,
        modelo_costos=CostosDirectosGore,
        modelo_personal=PersonalDirectoGORE,
        items_y_campos=items_y_campos_directos,
        calidades_y_campos=calidades_y_campos_directos,
        campos_costos_justificar=campos_directos,
        tipo_modelo='directo',
        **kwargs
    )


@receiver([post_save, post_delete], sender=CostosIndirectosGore)
@receiver([post_save, post_delete], sender=PersonalIndirectoGORE)
def handler_indirecto(sender, instance, **kwargs):
    actualizar_campos_paso3(
        sender=sender,
        instance=instance,
        modelo_costos=CostosIndirectosGore,
        modelo_personal=PersonalIndirectoGORE,
        items_y_campos=items_y_campos_indirectos,
        calidades_y_campos=calidades_y_campos_indirectos,
        campos_costos_justificar=campos_indirectos,
        tipo_modelo='indirecto',
        **kwargs
    )


@receiver(post_save, sender=CostosDirectosGore)
@receiver(post_save, sender=CostosIndirectosGore)
def actualizar_recursos_comparados(sender, instance, **kwargs):
    subtitulos_deseados = ["Sub. 22", "Sub. 29"]
    subtitulos_ids = Subtitulos.objects.filter(subtitulo__in=subtitulos_deseados).values_list('id', flat=True)

    if instance.item_subtitulo and instance.item_subtitulo.subtitulo_id not in subtitulos_ids:
        return

    # Identifica el ItemSubtitulo y FormularioGORE asociados con la instancia de costo
    item_subtitulo = instance.item_subtitulo
    formulario_gore = instance.formulario_gore

    # Calcula los totales para costos directos e indirectos
    total_anual_sector_directo = \
        CostosDirectosGore.objects.filter(item_subtitulo=item_subtitulo, formulario_gore=formulario_gore).aggregate(
            Sum('total_anual_sector'))['total_anual_sector__sum'] or 0
    total_anual_sector_indirecto = \
        CostosIndirectosGore.objects.filter(item_subtitulo=item_subtitulo,
                                            formulario_gore=formulario_gore).aggregate(
            Sum('total_anual_sector'))['total_anual_sector__sum'] or 0

    total_anual_gore_directo = \
        CostosDirectosGore.objects.filter(item_subtitulo=item_subtitulo, formulario_gore=formulario_gore).aggregate(
            Sum('total_anual_gore'))['total_anual_gore__sum'] or 0
    total_anual_gore_indirecto = \
        CostosIndirectosGore.objects.filter(item_subtitulo=item_subtitulo,
                                            formulario_gore=formulario_gore).aggregate(
            Sum('total_anual_gore'))['total_anual_gore__sum'] or 0

    # Calcula los totales combinados
    costo_sector = total_anual_sector_directo + total_anual_sector_indirecto
    costo_gore = total_anual_gore_directo + total_anual_gore_indirecto

    # Actualiza o crea RecursosComparados solo si cumple la condición
    if (costo_gore > costo_sector):
        diferencia_monto = costo_gore - costo_sector
        RecursosComparados.objects.update_or_create(
            formulario_gore=formulario_gore,
            sector=instance.sector,
            item_subtitulo=item_subtitulo,
            defaults={
                'costo_sector': costo_sector,
                'costo_gore': costo_gore,
                'diferencia_monto': diferencia_monto
            }
        )


@receiver(post_save, sender=RecursosComparados)
def manejar_cambios_recursos_comparados(sender, instance, **kwargs):
    # Logica para SistemasInformaticos y RecursosFisicosInfraestructura

    # Sistemas Informaticos
    if instance.item_subtitulo.item == '07 - Programas Informáticos':
        SistemasInformaticos.objects.get_or_create(
            formulario_gore=instance.formulario_gore,
            sector=instance.sector,
            item_subtitulo=instance.item_subtitulo
        )

    # Recursos Fisicos Infraestructura
    subtitulos_deseados = ["Sub. 22", "Sub. 29"]
    subtitulos_ids = Subtitulos.objects.filter(subtitulo__in=subtitulos_deseados).values_list('id', flat=True)
    if instance.item_subtitulo.subtitulo_id in subtitulos_ids and instance.item_subtitulo.item != '07 - Programas Informáticos':
        RecursosFisicosInfraestructura.objects.get_or_create(
            formulario_gore=instance.formulario_gore,
            sector=instance.sector,
            item_subtitulo=instance.item_subtitulo
        )




'''@receiver(post_delete, sender=RecursosComparados)
@receiver(post_delete, sender=CostosIndirectosGore)
def eliminar_instancias_relacionadas(sender, instance, **kwargs):

    # Identificar y manejar la eliminación para Sistemas Informaticos y Recursos Fisicos Infraestructura
    programas_informaticos = ItemSubtitulo.objects.filter(item='07 - Programas Informáticos').first()
    if programas_informaticos and instance.item_subtitulo == programas_informaticos:
        SistemasInformaticos.objects.filter(
            formulario_gore=instance.formulario_gore,
            sector=instance.sector,
            item_subtitulo=programas_informaticos
        ).delete()

    # Excluir el item "07 - Programas Informáticos" para Recursos Fisicos Infraestructura
    if instance.item_subtitulo.subtitulo.subtitulo in subtitulos_deseados and instance.item_subtitulo != programas_informaticos:
        RecursosFisicosInfraestructura.objects.filter(
            formulario_gore=instance.formulario_gore,
            sector=instance.sector,
            item_subtitulo=instance.item_subtitulo
        ).delete()'''