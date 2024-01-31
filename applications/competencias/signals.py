from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5


@receiver(post_save, sender=Competencia)
@transaction.atomic
def crear_etapas_para_competencia(sender, instance, created, **kwargs):
    if created:
        # Crear etapas
        Etapa1.objects.get_or_create(competencia=instance)
        Etapa2.objects.get_or_create(competencia=instance)
        Etapa3.objects.get_or_create(competencia=instance)
        Etapa4.objects.get_or_create(competencia=instance)
        Etapa5.objects.get_or_create(competencia=instance)


@receiver(m2m_changed, sender=Competencia.usuarios_subdere.through)
def asignar_creador_a_subdere(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" and instance.creado_por:
        # Si el usuario creado_por no está en usuarios_subdere, añádelo
        if not instance.usuarios_subdere.filter(id=instance.creado_por.id).exists():
            instance.usuarios_subdere.add(instance.creado_por)


@receiver(post_save, sender=Etapa1)
def actualizar_estado_y_fecha_competencia(sender, instance, **kwargs):
    competencia = instance.competencia
    actualizar = False

    # Actualizar fecha_inicio si es necesario
    if instance.fecha_inicio and competencia.fecha_inicio != instance.fecha_inicio:
        competencia.fecha_inicio = instance.fecha_inicio
        actualizar = True

    # Guardar cambios en la competencia si ha habido algún cambio
    if actualizar:
        competencia.save()


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