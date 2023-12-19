from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, CoberturaAnual, ResumenCostosPorSubtitulo, \
    EvolucionGastoAsociado, VariacionPromedio, CostoAnio


@receiver(post_save, sender=FormularioSectorial)
def crear_coberturas_anuales(sender, instance, created, **kwargs):
    if created:
        año_actual = timezone.now().year
        año_inicial = año_actual - 5

        for año in range(año_inicial, año_actual):
            CoberturaAnual.objects.get_or_create(
                formulario_sectorial=instance,
                anio=año
            )


@receiver(post_save, sender=Competencia)
def actualizar_coberturas_anuales(sender, instance, **kwargs):
    año_actual = timezone.now().year
    año_inicial = año_actual - 5

    formularios_sectoriales = FormularioSectorial.objects.filter(competencia=instance)

    for formulario in formularios_sectoriales:
        for año in range(año_inicial, año_actual):
            CoberturaAnual.objects.get_or_create(
                formulario_sectorial=formulario,
                anio=año
            )