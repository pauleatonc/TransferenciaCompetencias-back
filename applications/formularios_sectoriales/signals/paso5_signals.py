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


@receiver(post_save, sender=CostosDirectos)
@receiver(post_save, sender=CostosIndirectos)
@receiver(post_delete, sender=CostosDirectos)
@receiver(post_delete, sender=CostosIndirectos)
def actualizar_resumen_costos(sender, instance, **kwargs):
    """
    Actualiza el resumen de costos por subtitulo cuando un CostosDirectos o CostosIndirectos
    es creado, actualizado o eliminado.
    """
    # Asumiendo que cada instancia de CostosDirectos o CostosIndirectos
    # está relacionada con exactamente un ItemSubtitulo
    if hasattr(instance, 'item_subtitulo'):
        formulario_sectorial_id = instance.formulario_sectorial_id
        subtitulo_id = instance.item_subtitulo.subtitulo_id
        ResumenCostosPorSubtitulo.actualizar_resumen(subtitulo_id, formulario_sectorial_id)



def actualizar_total_costos(model_cls, campo_costo_total, instance):
    """
    Actualiza el campo de costos totales (directos o indirectos) de Paso5.
    """
    if instance.formulario_sectorial:
        total = model_cls.objects.filter(
            formulario_sectorial=instance.formulario_sectorial
        ).aggregate(total=models.Sum('total_anual'))['total'] or 0

        Paso5.objects.filter(
            formulario_sectorial=instance.formulario_sectorial
        ).update(**{campo_costo_total: total})


@receiver(post_save, sender=CostosDirectos)
@receiver(post_delete, sender=CostosDirectos)
def actualizar_total_costos_directos(sender, instance, **kwargs):
    actualizar_total_costos(Paso5, 'total_costos_directos')


@receiver(post_save, sender=CostosIndirectos)
@receiver(post_delete, sender=CostosIndirectos)
def actualizar_total_costos_indirectos(sender, instance, **kwargs):
    actualizar_total_costos(Paso5, 'total_costos_indirectos')


def actualizar_costos_totales(formulario_sectorial_id):
    """
    Actualiza el campo costos_totales de Paso5 basándose en la suma de
    total_costos_directos y total_costos_indirectos.
    """
    paso5 = Paso5.objects.filter(formulario_sectorial_id=formulario_sectorial_id).first()
    if paso5:
        total_directos = paso5.total_costos_directos or 0
        total_indirectos = paso5.total_costos_indirectos or 0
        paso5.costos_totales = total_directos + total_indirectos
        paso5.save()


@receiver(post_save, sender=CostosDirectos)
@receiver(post_delete, sender=CostosDirectos)
@receiver(post_save, sender=CostosIndirectos)
@receiver(post_delete, sender=CostosIndirectos)
def actualizar_total_costos(sender, instance, **kwargs):
    """
    Llama a actualizar_costos_totales cada vez que se crea, actualiza o elimina
    una instancia de CostosDirectos o CostosIndirectos.
    """
    # Asegúrate de que 'instance' es una instancia del modelo correcto
    if isinstance(instance, (CostosDirectos, CostosIndirectos)):
        formulario_sectorial_id = instance.formulario_sectorial_id
        actualizar_costos_totales(formulario_sectorial_id)
    else:
        # Maneja el caso en el que 'instance' no es lo que esperabas
        print(f"Tipo de instancia inesperado: {type(instance)}")



@receiver(post_save, sender=ResumenCostosPorSubtitulo)
def crear_o_actualizar_gasto_y_variacion(sender, instance, created, **kwargs):
    # Crear o actualizar EvolucionGastoAsociado
    EvolucionGastoAsociado.objects.get_or_create(
        formulario_sectorial=instance.formulario_sectorial,
        subtitulo=instance.subtitulo
    )

    # Crear o actualizar VariacionPromedio
    VariacionPromedio.objects.get_or_create(
        formulario_sectorial=instance.formulario_sectorial,
        subtitulo=instance.subtitulo
    )


@receiver(post_save, sender=FormularioSectorial)
def crear_costos_anio(sender, instance, created, **kwargs):
    if created:
        año_actual = timezone.now().year
        año_inicial = año_actual - 5

        for año in range(año_inicial, año_actual):
            CostoAnio.objects.get_or_create(
                anio=año,
                defaults={'costo': 0}  # O el valor predeterminado que desees
            )
