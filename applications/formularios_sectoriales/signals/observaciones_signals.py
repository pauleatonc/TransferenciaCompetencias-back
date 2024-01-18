from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from applications.formularios_sectoriales.models import FormularioSectorial, ObservacionesSubdereFormularioSectorial


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        ObservacionesSubdereFormularioSectorial.objects.create(formulario_sectorial=instance)


@receiver(post_delete, sender=FormularioSectorial)
def eliminar_instancias_relacionadas(sender, instance, **kwargs):
    # Eliminar ObservacionesSubdereFormularioSectorial relacionadas
    ObservacionesSubdereFormularioSectorial.objects.filter(formulario_sectorial=instance).delete()
