from django.db.models.signals import post_save
from django.dispatch import receiver
from applications.formularios_sectoriales.models import Paso1, MarcoJuridico, OrganigramaRegional


@receiver(post_save, sender=Paso1)
def crear_relaciones_paso1(sender, instance, created, **kwargs):
    if created:
        # Crear una instancia de MarcoJuridico para el nuevo Paso1
        MarcoJuridico.objects.create(paso1=instance)

        # Crear una instancia de OrganigramaRegional para cada región asociada a la Competencia
        competencia = instance.formulario_sectorial.competencia
        for region in competencia.regiones.all():
            OrganigramaRegional.objects.create(paso1=instance, region=region)
