from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso1
)


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso1
        Paso1.objects.create(formulario_gore=instance)

