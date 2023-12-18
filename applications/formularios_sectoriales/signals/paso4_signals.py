from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import *

@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso4
        Paso4.objects.create(formulario_sectorial=instance)

        # Crear instancia de IndicadorDesempeno
        IndicadorDesempeno.objects.create(formulario_sectorial=instance)