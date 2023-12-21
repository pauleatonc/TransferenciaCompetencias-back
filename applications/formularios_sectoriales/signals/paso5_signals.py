from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.base import models
from applications.formularios_sectoriales.models import (
    CostosDirectos,
    CostosIndirectos,
    ResumenCostosPorSubtitulo,
    Paso5, EvolucionGastoAsociado, VariacionPromedio, CostoAnio, FormularioSectorial
)
from django.utils import timezone


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso5
        Paso5.objects.create(formulario_sectorial=instance)


@receiver(post_delete, sender=CostosDirectos)
def post_delete_costos_directos(sender, instance, **kwargs):
    # Verificar y eliminar del resumen si es necesario
    CostosDirectos.verificar_y_eliminar_resumen(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)

    # Actualizar el total de costos directos en Paso5
    CostosDirectos.actualizar_resumen_costos(instance)

    # Actualizar el total anual en ResumenCostosPorSubtitulo
    ResumenCostosPorSubtitulo.actualizar_total_anual(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)


@receiver(post_delete, sender=CostosIndirectos)
def post_delete_costos_indirectos(sender, instance, **kwargs):
    # Verificar y eliminar del resumen si es necesario
    CostosIndirectos.verificar_y_eliminar_resumen(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)

    # Actualizar el total de costos indirectos en Paso5
    CostosIndirectos.actualizar_resumen_costos(instance)

    # Actualizar el total anual en ResumenCostosPorSubtitulo
    ResumenCostosPorSubtitulo.actualizar_total_anual(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)
