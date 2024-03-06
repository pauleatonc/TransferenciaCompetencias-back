from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso2,
    CostosDirectosGore,
    CostosIndirectosGore
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
    # Verifica si el subtítulo asociado es 'Sub. 21'
    if instance.item_subtitulo.subtitulo.subtitulo == 'Sub. 21':
        # No hacer nada si el subtítulo es 'Sub. 21'
        return

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



