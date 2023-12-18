from django.db.models.signals import post_save
from django.dispatch import receiver
from applications.formularios_sectoriales.models import MarcoJuridico, OrganigramaRegional, FormularioSectorial


@receiver(post_save, sender=FormularioSectorial)
def crear_relaciones_formulario(sender, instance, created, **kwargs):
    if created:
        # Crear una instancia de MarcoJuridico para el nuevo FormularioSectorial
        MarcoJuridico.objects.create(formulario_sectorial=instance)

