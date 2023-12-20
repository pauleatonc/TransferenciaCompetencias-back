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
    CostosDirectos.verificar_y_eliminar_resumen(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)


@receiver(post_delete, sender=CostosIndirectos)
def post_delete_costos_indirectos(sender, instance, **kwargs):
    CostosIndirectos.verificar_y_eliminar_resumen(instance.item_subtitulo.subtitulo_id, instance.formulario_sectorial_id)