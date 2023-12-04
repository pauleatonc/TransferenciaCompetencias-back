from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from django.utils import timezone

from applications.etapas.models import Etapa2, Etapa3
from applications.formularios_gores.models import FormularioGORE
from applications.regioncomuna.models import Region




@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa3_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        etapa2 = Etapa2.objects.filter(competencia=instance).first()
        etapa3 = Etapa3.objects.filter(competencia=instance).first()

        if etapa3:
            etapa3.usuario_notificado = instance.usuarios_dipres.exists()

            # Verificar si etapa2 está aprobada
            if etapa3.usuario_notificado and etapa2 and etapa2.aprobada:
                etapa3.fecha_inicio = timezone.now()

            etapa3.save()


@receiver(post_save, sender=Etapa2)
def establecer_fecha_inicio_etapa3_al_aprobar_etapa2(sender, instance, created, **kwargs):
    if not created and instance.aprobada:
        etapa3 = Etapa3.objects.filter(competencia=instance.competencia).first()

        if etapa3 and etapa3.usuario_notificado and not etapa3.fecha_inicio:
            etapa3.fecha_inicio = timezone.now()
            etapa3.save()