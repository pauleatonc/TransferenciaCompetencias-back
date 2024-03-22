from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from applications.formularios_gores.models import ObservacionesSubdereFormularioGORE, FormularioGORE


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        ObservacionesSubdereFormularioGORE.objects.create(formulario_sectorial=instance)