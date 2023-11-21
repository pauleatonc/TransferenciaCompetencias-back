from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.etapas.models import Etapa1
from applications.etapas.models.etapa2 import Etapa2


@receiver(post_save, sender=Etapa1)
def actualizar_etapa2(sender, instance, **kwargs):
    if instance.estado == 'finalizada':
        # Obtener o crear la instancia de Etapa2 asociada
        etapa2, created = Etapa2.objects.get_or_create(competencia=instance.competencia)

        # Actualizar estado y tiempo restante
        etapa2.usuarios_notificados = True
        if not etapa2.fecha_inicio:
            etapa2.fecha_inicio = timezone.now()

        etapa2.plazo_dias = instance.competencia.plazo_formulario_sectorial

        etapa2.save()