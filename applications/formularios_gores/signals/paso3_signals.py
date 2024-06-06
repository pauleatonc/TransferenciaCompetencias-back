from django.db import transaction
from django.db.models import Sum, Q
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
import time

from applications.competencias.models import Competencia
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
from applications.regioncomuna.models import Region


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso3
        Paso3.objects.create(formulario_gore=instance)


@transaction.atomic
def eliminar_formularios_y_anidados(competencia, region_pk):
    formularios_gore = FormularioGORE.objects.filter(competencia=competencia, region_id=region_pk)
    for formulario in formularios_gore:
        # Eliminar instancias anidadas antes de eliminar el formulario GORE
        PersonalDirectoGORE.objects.filter(formulario_gore=formulario).delete()
        PersonalIndirectoGORE.objects.filter(formulario_gore=formulario).delete()
        RecursosComparados.objects.filter(formulario_gore=formulario).delete()
        SistemasInformaticos.objects.filter(formulario_gore=formulario).delete()
        RecursosFisicosInfraestructura.objects.filter(formulario_gore=formulario).delete()
        formulario.delete()


@receiver(m2m_changed, sender=Competencia.regiones.through)
@transaction.atomic
def modificar_formulario_gore_por_region(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        competencia = Competencia.objects.get(pk=instance.pk)
        for region_pk in pk_set:
            region = Region.objects.get(pk=region_pk)
            FormularioGORE.objects.get_or_create(
                competencia=competencia,
                region=region,
                defaults={'nombre': f'Formulario GORE de {region.region} - {competencia.nombre}'}
            )
    elif action == 'post_remove':
        competencia = Competencia.objects.get(pk=instance.pk)
        for region_pk in pk_set:
            eliminar_formularios_y_anidados(competencia, region_pk)


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
            'numero_personas_sectorial': instance.numero_personas,
            'total_rentas': instance.total_rentas
        }

    formulario_sectorial = instance.formulario_sectorial
    competencia = formulario_sectorial.competencia
    sector = formulario_sectorial.sector
    region = instance.region  # Aseguramos que se utilice la región correspondiente

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia, region=region)
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
    "04 - Otros Gastos en Personal".
    """
    # Manejar la creación o actualización de costos
    if instance.item_subtitulo and instance.sector is None:
        item_subtitulo_texto = instance.item_subtitulo.item
        calidades = relacion_item_calidad.get(item_subtitulo_texto, [])

        if item_subtitulo_texto == "04 - Otros Gastos en Personal" and not created:
            # Si estamos actualizando y es el caso especial "04 - Otros Gastos en Personal",
            # verifica si se deben eliminar instancias de personal asociadas
            if not modelo_costos.objects.filter(item_subtitulo=instance.item_subtitulo, sector__isnull=True).exists():
                # No hay más costos asociados a este ítem, eliminar todas las instancias de personal relacionadas
                personal_asociado = modelo_personal.objects.filter(
                    formulario_gore=instance.formulario_gore,
                    calidad_juridica__in=[CalidadJuridica.objects.get(calidad_juridica=calidad) for calidad in calidades]
                )
                personal_asociado.delete()
            return  # Finaliza la ejecución para este caso

        if not isinstance(calidades, list):
            calidades = [calidades]

        for calidad in calidades:
            calidad_juridica_obj, _ = CalidadJuridica.objects.get_or_create(calidad_juridica=calidad)
            # Solo crea la instancia de personal si aún no existe y no es el caso especial "04 - Otros Gastos en Personal"
            if not modelo_personal.objects.filter(formulario_gore=instance.formulario_gore,
                                                  calidad_juridica=calidad_juridica_obj).exists():
                modelo_personal.objects.create(
                    formulario_gore=instance.formulario_gore,
                    calidad_juridica=calidad_juridica_obj
                )

def eliminar_instancias_personal(modelo_costos, modelo_personal, instance):
    """
    Elimina instancias asociadas a los ítems si ya no existen costos vinculados.
    """

    # Eliminación de instancias de personal que ya no tienen costos asociados.
    for calidad, _ in relacion_item_calidad.items():
        calidades = relacion_item_calidad[calidad] if isinstance(relacion_item_calidad[calidad], list) else [relacion_item_calidad[calidad]]
        for calidad in calidades:
            try:
                calidad_juridica_obj = CalidadJuridica.objects.get(calidad_juridica=calidad)
                if not modelo_costos.objects.filter(formulario_gore=instance.formulario_gore,
                                                    item_subtitulo__item=calidad, sector__isnull=True).exists():
                    modelo_personal.objects.filter(formulario_gore=instance.formulario_gore,
                                                   calidad_juridica=calidad_juridica_obj).delete()
            except CalidadJuridica.DoesNotExist:
                continue


@receiver(post_save, sender=CostosDirectosGore)
def actualizar_personal_directo(sender, instance, **kwargs):
    actualizar_instancias_personal(CostosDirectosGore, PersonalDirectoGORE, instance)


@receiver(post_delete, sender=CostosDirectosGore)
def eliminar_personal_directo(sender, instance, **kwargs):
    eliminar_instancias_personal(CostosDirectosGore, PersonalDirectoGORE, instance)


@receiver(post_save, sender=CostosIndirectosGore)
def actualizar_personal_indirecto(sender, instance, **kwargs):
    actualizar_instancias_personal(CostosIndirectosGore, PersonalIndirectoGORE, instance)


@receiver(post_delete, sender=CostosIndirectosGore)
def eliminar_personal_indirecto(sender, instance, **kwargs):
    eliminar_instancias_personal(CostosIndirectosGore, PersonalIndirectoGORE, instance)


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
    # Primero, verifica si instance.item_subtitulo existe y no es None
    if instance.item_subtitulo is None:
        return

    # Segundo, verifica si el subtitulo del ItemSubtitulo es el deseado y crea instancias de RecursosComparados
    # que cumplan el criterio
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


@receiver([post_save, post_delete], sender=RecursosComparados)
def manejar_cambios_recursos_comparados(sender, instance, **kwargs):
    # Sistemas Informáticos
    if instance.item_subtitulo and instance.item_subtitulo.item == '07 - Programas Informáticos':
        existen_recursos = RecursosComparados.objects.filter(
            formulario_gore=instance.formulario_gore,
            item_subtitulo__item='07 - Programas Informáticos'
        ).exists()

        if existen_recursos:
            # Asegúrate de crear la instancia solo si no existe.
            SistemasInformaticos.objects.get_or_create(
                formulario_gore=instance.formulario_gore,
                item_subtitulo=instance.item_subtitulo
            )
        else:
            # Elimina todas las instancias de SistemasInformaticos si no existen RecursosComparados correspondientes.
            SistemasInformaticos.objects.filter(
                formulario_gore=instance.formulario_gore,
                item_subtitulo=instance.item_subtitulo
            ).delete()

    # Recursos Fisicos Infraestructura
    subtitulos_deseados = ["Sub. 22", "Sub. 29"]
    subtitulos_ids = Subtitulos.objects.filter(subtitulo__in=subtitulos_deseados).values_list('id', flat=True)

    if instance.item_subtitulo and instance.item_subtitulo.subtitulo_id in subtitulos_ids:
        # Excepción para no manejar '07 - Programas Informáticos' en RecursosFisicosInfraestructura
        if instance.item_subtitulo.item != '07 - Programas Informáticos':
            existen_recursos = RecursosComparados.objects.filter(
                formulario_gore=instance.formulario_gore,
                item_subtitulo__subtitulo_id__in=subtitulos_ids
            ).exists()

        if existen_recursos:
            # Asegúrate de crear la instancia solo si no existe.
            RecursosFisicosInfraestructura.objects.get_or_create(
                formulario_gore=instance.formulario_gore,
                item_subtitulo=instance.item_subtitulo
            )
        else:
            # Elimina todas las instancias de RecursosFisicosInfraestructura si no existen RecursosComparados correspondientes.
            RecursosFisicosInfraestructura.objects.filter(
                formulario_gore=instance.formulario_gore,
                item_subtitulo=instance.item_subtitulo
            ).delete()


@receiver([post_save, post_delete], sender=RecursosComparados)
def actualizar_diferencias_recursos_comparados(sender, instance, **kwargs):
    if not instance.formulario_gore.paso3_gore:
        # Crea la instancia de Paso3 si no existe
        Paso3.objects.create(formulario_gore=instance.formulario_gore)

    paso3 = instance.formulario_gore.paso3_gore
    for subtitulo in ['22', '29']:
        subtitulos_ids = Subtitulos.objects.filter(subtitulo__startswith=f'Sub. {subtitulo}').values_list('id',
                                                                                                          flat=True)
        diferencia_monto = RecursosComparados.objects.filter(
            item_subtitulo__subtitulo_id__in=subtitulos_ids,
            formulario_gore=instance.formulario_gore
        ).aggregate(Sum('diferencia_monto'))['diferencia_monto__sum'] or 0

        setattr(paso3, f'subtitulo_{subtitulo}_diferencia_sector', diferencia_monto)
    paso3.save()


def actualizar_justificados_gore(formulario_gore):
    paso3 = formulario_gore.paso3_gore
    if not paso3:
        # Crea la instancia de Paso3 si no existe
        Paso3.objects.create(formulario_gore=formulario_gore)

    for subtitulo in ['22', '29']:
        subtitulos_ids = Subtitulos.objects.filter(subtitulo__startswith=f'Sub. {subtitulo}').values_list('id',
                                                                                                          flat=True)

        costo_total_rf = RecursosFisicosInfraestructura.objects.filter(
            item_subtitulo__subtitulo_id__in=subtitulos_ids,
            formulario_gore=formulario_gore
        ).aggregate(Sum('costo_total'))['costo_total__sum'] or 0

        if subtitulo == '29':
            costo_total_si = SistemasInformaticos.objects.filter(
                formulario_gore=formulario_gore
            ).aggregate(Sum('costo'))['costo__sum'] or 0
            costo_total_rf += costo_total_si

        setattr(paso3, f'subtitulo_{subtitulo}_justificados_gore', costo_total_rf)
    paso3.save()


@receiver([post_save, post_delete], sender=RecursosFisicosInfraestructura)
@receiver([post_save, post_delete], sender=SistemasInformaticos)
def actualizar_justificados_por_subtitulos(sender, instance, **kwargs):
    actualizar_justificados_gore(instance.formulario_gore)


def actualizar_subtitulo_21(sender, instance, **kwargs):
    formulario_gore = instance.formulario_gore
    paso3_instance = Paso3.objects.get(formulario_gore=formulario_gore)

    suma_directo = PersonalDirectoGORE.objects.filter(
        formulario_gore=formulario_gore,
        sector__isnull=True
    ).aggregate(suma_renta_bruta=Sum('renta_bruta'))['suma_renta_bruta'] or 0

    suma_indirecto = PersonalIndirectoGORE.objects.filter(
        formulario_gore=formulario_gore,
        sector__isnull=True
    ).aggregate(suma_total_rentas=Sum('total_rentas'))['suma_total_rentas'] or 0

    paso3_instance.subtitulo_21_justificados_gore = suma_directo + suma_indirecto
    paso3_instance.save()


'''@receiver(post_save, sender=PersonalDirectoGORE)
@receiver(post_save, sender=PersonalIndirectoGORE)
@receiver(post_delete, sender=PersonalDirectoGORE)
@receiver(post_delete, sender=PersonalIndirectoGORE)
def actualizar_subtitulo_21_signal(sender, instance, **kwargs):
    actualizar_subtitulo_21(sender, instance)
'''