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

id_generado = int(time.time())

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
            'total_rentas': instance.total_rentas,
            # Añade aquí cualquier otro campo específico de PersonalIndirecto
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
            # Asegúrate de que 'id' aquí es el campo correcto para buscar la instancia.
            # Si es necesario, usa un campo diferente que sea único y relevante.
            id=instance.id,
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
    modelo_gore.objects.filter(id=instance.id).delete()


def get_item_subtitulo(item):
    return ItemSubtitulo.objects.get(item=item)


def get_calidad_juridica(calidad):
    return CalidadJuridica.objects.get(calidad_juridica=calidad)


def calcular_total_por_item(modelo, paso3_gore_instance, item_subtitulo):
    return sum((item.total_anual_gore or 0) for item in modelo.objects.filter(
        formulario_gore=paso3_gore_instance.formulario_gore,
        item_subtitulo=item_subtitulo
    ))


def calcular_costos_por_justificar(paso3_gore_instance, campos):
    """
    Calcula los costos por justificar y actualiza la instancia de Paso3_gore.

    :param paso3_gore_instance: La instancia de Paso3 que se está actualizando.
    :param campos: Diccionario con la configuración de los campos a calcular.
    """
    for campo_total, campo_justificado, campo_por_justificar in campos:
        total = getattr(paso3_gore_instance, campo_total) or 0
        justificado = getattr(paso3_gore_instance, campo_justificado) or 0
        por_justificar = total - justificado
        setattr(paso3_gore_instance, campo_por_justificar, por_justificar)


def calcular_total_por_calidad_directo(modelo, paso3_gore_instance, calidad_juridica):
    return sum((personal.renta_bruta or 0) for personal in modelo.objects.filter(
        formulario_gore=paso3_gore_instance.formulario_gore,
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


@receiver([post_save, post_delete], sender=CostosDirectosGore)
@receiver([post_save, post_delete], sender=PersonalDirectoGORE)
# Realiza los cálculos de los campos directos y los costos por justificar
def actualizar_campos_paso3_directo(sender, instance, **kwargs):
    # Verifica si la instancia tiene un valor asignado en el campo sector y retorna si es así
    if instance.sector is not None:
        return

    if isinstance(instance, Paso3):
        return

    paso3_instance = Paso3.objects.get(formulario_gore=instance.formulario_gore)
    total_especifico = 0

    for item, campo in items_y_campos_directos.items():
        item_subtitulo = get_item_subtitulo(item)
        total = calcular_total_por_item(CostosDirectosGore, paso3_instance, item_subtitulo)
        setattr(paso3_instance, campo, total)

    for calidad, campo in calidades_y_campos_directos.items():
        calidad_juridica = get_calidad_juridica(calidad)
        total = calcular_total_por_calidad_directo(PersonalDirectoGORE, paso3_instance, calidad_juridica)
        setattr(paso3_instance, campo, total)
        total_especifico += total  # Acumula los totales específicos

    # Calcular el total general de todas las calidades
    total_general = sum(
        (personal.renta_bruta or 0) for personal in PersonalDirectoGORE.objects.filter(
            formulario_gore=paso3_instance.formulario_gore
        )
    )

    # Calcular el total de "otras calidades"
    total_otras_calidades = total_general - total_especifico
    paso3_instance.sub21_gastos_en_personal_justificado = total_otras_calidades

    """ Calcula los costos por justificar en cada caso: Planta, Contrata, resto de calidades juridicas"""

    campos_directos = [
        ('sub21_total_personal_planta', 'sub21_personal_planta_justificado', 'sub21_personal_planta_justificar'),
        ('sub21_total_personal_contrata', 'sub21_personal_contrata_justificado', 'sub21_personal_contrata_justificar'),
        ('sub21_total_otras_remuneraciones', 'sub21_otras_remuneraciones_justificado',
         'sub21_otras_remuneraciones_justificar'),
        ('sub21_total_gastos_en_personal', 'sub21_gastos_en_personal_justificado',
         'sub21_gastos_en_personal_justificar'),
    ]

    calcular_costos_por_justificar(paso3_instance, campos_directos)

    paso3_instance.save()


def calcular_total_por_calidad_indirecto(modelo, paso3_gore_instance, calidad_juridica):
    return sum((personal.total_rentas or 0) for personal in modelo.objects.filter(
        formulario_gore=paso3_gore_instance.formulario_gore,
        calidad_juridica=calidad_juridica
    ))


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


@receiver([post_save, post_delete], sender=CostosIndirectosGore)
@receiver([post_save, post_delete], sender=PersonalIndirectoGORE)
# Realiza los cálculos de los campos indirectos y los costos por justificar
def actualizar_campos_paso3_indirecto(sender, instance, **kwargs):
    # Verifica si la instancia tiene un valor asignado en el campo sector y retorna si es así
    if instance.sector is not None:
        return

    if isinstance(instance, Paso3):
        return

    paso3_instance = Paso3.objects.get(formulario_gore=instance.formulario_gore)
    total_especifico = 0

    for item, campo in items_y_campos_indirectos.items():
        item_subtitulo = get_item_subtitulo(item)
        total = calcular_total_por_item(CostosIndirectosGore, paso3_instance, item_subtitulo)
        setattr(paso3_instance, campo, total)

    for calidad, campo in calidades_y_campos_indirectos.items():
        calidad_juridica = get_calidad_juridica(calidad)
        total = calcular_total_por_calidad_indirecto(PersonalIndirectoGORE, paso3_instance, calidad_juridica)
        setattr(paso3_instance, campo, total)
        total_especifico += total  # Acumula los totales específicos

    # Calcular el total general de todas las calidades
    total_general = sum(
        (personal.total_rentas or 0) for personal in PersonalIndirectoGORE.objects.filter(
            formulario_gore=paso3_instance.formulario_gore
        )
    )

    # Calcular el total de "otras calidades"
    total_otras_calidades = total_general - total_especifico
    paso3_instance.sub21b_gastos_en_personal_justificado = total_otras_calidades

    """ Calcula los costos por justificar en cada caso: Planta, Contrata, resto de calidades juridicas"""

    campos_indirectos = [
        ('sub21b_total_personal_planta', 'sub21b_personal_planta_justificado', 'sub21b_personal_planta_justificar'),
        ('sub21b_total_personal_contrata', 'sub21b_personal_contrata_justificado',
         'sub21b_personal_contrata_justificar'),
        ('sub21b_total_otras_remuneraciones', 'sub21b_otras_remuneraciones_justificado',
         'sub21b_otras_remuneraciones_justificar'),
        ('sub21b_total_gastos_en_personal', 'sub21b_gastos_en_personal_justificado',
         'sub21b_gastos_en_personal_justificar'),
    ]

    calcular_costos_por_justificar(paso3_instance, campos_indirectos)
    paso3_instance.save()


# Mapeo entre ItemSubtitulo y CalidadJuridica
relacion_item_calidad = {
    "01 - Personal de Planta": "Planta",
    "02 - Personal de Contrata": "Contrata",
    "03 - Otras Remuneraciones": "Honorario a suma alzada",
    "04 - Otros Gastos en Personal": ["Honorario asimilado a grado", "Comisión de servicio", "Otro"],
}


def crear_instancias_personal(modelo_costos, modelo_personal, instance, created):
    # Crea instancias para los modelos de PersonalDirecto y PersonalIndirecto en relación con la creación de
    # Costos Directos e Indirectos
    if created:
        item_subtitulo_texto = instance.item_subtitulo.item
        calidades = relacion_item_calidad.get(item_subtitulo_texto)

        if item_subtitulo_texto == "04 - Otros Gastos en Personal":
            return  # No se crean instancias para este caso

        if calidades:
            if not isinstance(calidades, list):
                calidades = [calidades]

            for calidad in calidades:
                calidad_juridica_obj, _ = CalidadJuridica.objects.get_or_create(calidad_juridica=calidad)
                if not modelo_personal.objects.filter(formulario_gore=instance.formulario_gore,
                                                      calidad_juridica=calidad_juridica_obj).exists():

                    modelo_personal.objects.create(
                        id=id_generado,
                        formulario_gore=instance.formulario_gore,
                        calidad_juridica=calidad_juridica_obj
                    )


def eliminar_instancias_personal(modelo_costos, modelo_personal, instance):
    item_subtitulo_texto = instance.item_subtitulo.item
    calidades = relacion_item_calidad.get(item_subtitulo_texto)

    if calidades:
        if not isinstance(calidades, list):
            calidades = [calidades]

        for calidad in calidades:
            calidad_juridica_obj = CalidadJuridica.objects.get(calidad_juridica=calidad)
            existe_costo = modelo_costos.objects.filter(formulario_gore=instance.formulario_gore,
                                                        item_subtitulo=instance.item_subtitulo).exists()

            if not existe_costo:
                modelo_personal.objects.filter(formulario_gore=instance.formulario_gore,
                                               calidad_juridica=calidad_juridica_obj).delete()


@receiver(post_save, sender=CostosDirectosGore)
def post_save_costos_directos(sender, instance, created, **kwargs):
    # Verifica si el sector es null o vacío antes de proceder
    if instance.sector is None:
        crear_instancias_personal(CostosDirectosGore, PersonalDirectoGORE, instance, created)


@receiver(post_delete, sender=CostosDirectosGore)
def post_delete_costos_directos(sender, instance, **kwargs):
    # Verifica si el sector es null o vacío antes de proceder
    if instance.sector is None:
        eliminar_instancias_personal(CostosDirectosGore, PersonalDirectoGORE, instance)


@receiver(post_save, sender=CostosIndirectosGore)
def post_save_costos_indirectos(sender, instance, created, **kwargs):
    # Verifica si el sector es null o vacío antes de proceder
    if instance.sector is None:
        crear_instancias_personal(CostosIndirectosGore, PersonalIndirectoGORE, instance, created)


@receiver(post_delete, sender=CostosIndirectosGore)
def post_delete_costos_indirectos(sender, instance, **kwargs):
    # Verifica si el sector es null o vacío antes de proceder
    if instance.sector is None:
        eliminar_instancias_personal(CostosIndirectosGore, PersonalIndirectoGORE, instance)


@receiver(post_save, sender=CostosDirectosGore)
@receiver(post_save, sender=CostosIndirectosGore)
def copiar_a_recursos_comparados_y_mas(sender, instance, **kwargs):
    subtitulos_deseados = ["Sub. 22", "Sub. 29"]
    programas_informaticos = ItemSubtitulo.objects.filter(item='07 - Programas Informáticos').first()
    subtitulos_ids = Subtitulos.objects.filter(subtitulo__in=subtitulos_deseados).values_list('id', flat=True)

    # Manejo de Recursos Comparados
    if instance.item_subtitulo.subtitulo_id in subtitulos_ids and (instance.total_anual_gore or 0) > (instance.total_anual_sector or 0):
        RecursosComparados.objects.update_or_create(
            formulario_gore=instance.formulario_gore,
            id=id_generado,
            sector=instance.sector,
            item_subtitulo=instance.item_subtitulo,
            defaults={
                'costo_sector': instance.total_anual_sector,
                'costo_gore': instance.total_anual_gore,
                'diferencia_monto': (instance.total_anual_gore or 0) - (instance.total_anual_sector or 0)
            }
        )

    # Manejo de Sistemas Informaticos
    if programas_informaticos and instance.item_subtitulo == programas_informaticos:
        SistemasInformaticos.objects.get_or_create(
            id=id_generado,
            formulario_gore=instance.formulario_gore,
            sector=instance.sector,
            item_subtitulo=programas_informaticos
        )

    # Manejo de Recursos Fisicos Infraestructura
    item_subtitulos_excluidos = ItemSubtitulo.objects.filter(
        Q(subtitulo_id__in=subtitulos_ids) & ~Q(id=programas_informaticos.id)
    )
    for item_subtitulo in item_subtitulos_excluidos:
        if instance.item_subtitulo == item_subtitulo:
            RecursosFisicosInfraestructura.objects.get_or_create(
                id=id_generado,
                formulario_gore=instance.formulario_gore,
                sector=instance.sector,
                item_subtitulo=item_subtitulo
            )


@receiver(post_delete, sender=CostosDirectosGore)
@receiver(post_delete, sender=CostosIndirectosGore)
def eliminar_instancias_relacionadas(sender, instance, **kwargs):
    # Identificar si el subtitulo de la instancia eliminada es "Sub. 22" o "Sub. 29"
    subtitulos_deseados = ["Sub. 22", "Sub. 29"]
    if instance.item_subtitulo.subtitulo.subtitulo in subtitulos_deseados:
        # Eliminar RecursosComparados correspondientes
        RecursosComparados.objects.filter(
            formulario_gore=instance.formulario_gore,
            sector=instance.sector,
            item_subtitulo=instance.item_subtitulo
        ).delete()

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
        ).delete()