from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5


@receiver(post_save, sender=Competencia)
@transaction.atomic
def crear_etapas_para_competencia(sender, instance, created, **kwargs):
    if created:
        # Crear etapas
        Etapa1.objects.get_or_create(competencia=instance)
        Etapa2.objects.get_or_create(competencia=instance, plazo_dias=instance.plazo_formulario_sectorial)
        Etapa3.objects.get_or_create(competencia=instance, plazo_dias=15)
        Etapa4.objects.get_or_create(competencia=instance, plazo_dias=instance.plazo_formulario_gore)
        Etapa5.objects.get_or_create(competencia=instance, plazo_dias=15)


@receiver(post_save, sender=Etapa5)
def actualizar_fecha_fin_y_estado_competencia(sender, instance, **kwargs):
    # Verifica si etapa5 ha sido aprobada
    if instance.aprobada:
        competencia = instance.competencia

        # Actualizar fecha_fin y estado de la competencia
        competencia.fecha_fin = timezone.now()
        competencia.estado = 'FIN'

        # Guarda los cambios en la competencia
        competencia.save()