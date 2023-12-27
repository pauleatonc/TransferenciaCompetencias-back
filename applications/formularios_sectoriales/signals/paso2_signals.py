from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import *

@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso2
        Paso2.objects.create(formulario_sectorial=instance)

        # Crear instancia de OrganismosIntervinientes
        organismo_interviniente = OrganismosIntervinientes.objects.create(
            formulario_sectorial=instance,
            organismo='MIN',
            sector_ministerio_servicio=instance.sector
        )

        # Crear instancia de PlataformasySoftwares
        PlataformasySoftwares.objects.create(formulario_sectorial=instance)

        # Crear instancia de FlujogramaCompetencia
        FlujogramaCompetencia.objects.create(formulario_sectorial=instance)


@receiver(post_save, sender=OrganismosIntervinientes)
def create_related_unidad(sender, instance, created, **kwargs):
    if created:
        UnidadesIntervinientes.objects.create(
            organismo=instance,
            formulario_sectorial=instance.formulario_sectorial
        )
