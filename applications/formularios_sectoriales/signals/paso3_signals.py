from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, CoberturaAnual


@receiver(post_save, sender=FormularioSectorial)
def crear_coberturas_anuales(sender, instance, created, **kwargs):
    if created:
        competencia = instance.competencia
        if competencia.fecha_inicio:
            año_actual = timezone.now().year
            año_inicio = competencia.fecha_inicio.year
            año_inicial = min(año_inicio, año_actual)

            for año in range(año_inicial - 4, año_inicial + 1):
                CoberturaAnual.objects.get_or_create(
                    formulario_sectorial=instance,
                    anio=año
                )

@receiver(post_save, sender=Competencia)
def actualizar_coberturas_anuales(sender, instance, **kwargs):
    if instance.fecha_inicio:
        año_actual = timezone.now().year
        año_inicio = instance.fecha_inicio.year
        año_inicial = min(año_inicio, año_actual)

        formularios_sectoriales = FormularioSectorial.objects.filter(competencia=instance)

        for formulario in formularios_sectoriales:
            for año in range(año_inicial - 4, año_inicial + 1):
                CoberturaAnual.objects.get_or_create(
                    formulario_sectorial=formulario,
                    anio=año
                )