from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso2,
    CostosDirectosGore as CostosDirectosGORE,
    CostosIndirectosGore as CostosIndirectosGORE,
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

@receiver(post_delete, sender=CostosDirectosSectorial)
def eliminar_costos_directos_gore_correspondiente(sender, instance, **kwargs):
    # Asumiendo que `instance` es una instancia de CostosDirectos de formulario_sectorial
    sectorial_sector = instance.formulario_sectorial.sector
    # Buscar y eliminar instancias de CostosDirectos de FormularioGORE con el mismo sector
    CostosDirectosGORE.objects.filter(
        formulario_gore__competencia=instance.formulario_sectorial.competencia,
        sector=sectorial_sector
    ).delete()


@receiver(post_save, sender=CostosDirectosSectorial)
def actualizar_costos_directos_gore(sender, instance, created, **kwargs):
    if not created:
        # Encuentra instancias relacionadas en CostosDirectosGORE
        costos_directos_gore_relacionados = CostosDirectosGORE.objects.filter(
            formulario_gore__competencia=instance.formulario_sectorial.competencia,
            sector=instance.formulario_sectorial.sector
        )

        for costo_gore in costos_directos_gore_relacionados:
            # Actualizar campos específicos
            if costo_gore.item_subtitulo != instance.item_subtitulo:
                costo_gore.item_subtitulo = instance.item_subtitulo
            if costo_gore.total_anual_sector != instance.total_anual:
                costo_gore.total_anual_sector = instance.total_anual
            costo_gore.save()

    if created:
        formulario_sectorial = instance.formulario_sectorial
        competencia = formulario_sectorial.competencia
        formularios_gore = FormularioGORE.objects.filter(competencia=competencia)

        for formulario_gore in formularios_gore:
            CostosDirectosGORE.objects.create(
                formulario_gore=formulario_gore,
                sector=formulario_sectorial.sector,
                item_subtitulo=instance.item_subtitulo,
                total_anual_sector=instance.total_anual
            )


