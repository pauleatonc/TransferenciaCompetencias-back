from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from django.utils import timezone

from applications.etapas.models import Etapa4, Etapa5


@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa5_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        etapa4 = Etapa4.objects.filter(competencia=instance).first()
        etapa5 = Etapa5.objects.filter(competencia=instance).first()

        if etapa5:
            etapa5.usuario_notificado = instance.usuarios_dipres.exists()

            # Verificar si etapa4 está aprobada
            if etapa5.usuario_notificado and etapa4 and etapa4.aprobada:
                etapa5.fecha_inicio = timezone.now()

            etapa5.save()


@receiver(post_save, sender=Etapa4)
def establecer_fecha_inicio_etapa5_al_aprobar_etapa4(sender, instance, created, **kwargs):
    if not created and instance.aprobada:
        etapa5 = Etapa5.objects.filter(competencia=instance.competencia).first()

        if etapa5 and etapa5.usuario_notificado and not etapa5.fecha_inicio:
            etapa5.fecha_inicio = timezone.now()
            etapa5.save()