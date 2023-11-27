from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from django.utils import timezone

from applications.etapas.models import Etapa3, Etapa4


@receiver(m2m_changed, sender=Competencia.usuarios_gore.through)
def actualizar_etapa4_al_modificar_usuarios_gore(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        etapa3 = instance.etapa3_set.first()
        etapa4 = instance.etapa4_set.first()

        if etapa4:
            todos_los_usuarios_asignados = True
            for region in instance.regiones.all():
                if not instance.usuarios_gore.filter(region=region).exists():
                    todos_los_usuarios_asignados = False
                    break

            etapa4.usuarios_notificados = todos_los_usuarios_asignados

            # Fijar fecha_inicio si etapa3 está aprobada
            if todos_los_usuarios_asignados and etapa3 and etapa3.aprobada:
                etapa4.fecha_inicio = timezone.now()

            etapa4.save()


@receiver(post_save, sender=Etapa3)
def establecer_fecha_inicio_etapa4_al_aprobar_etapa3(sender, instance, created, **kwargs):
    if not created and instance.aprobada:
        etapa4 = Etapa4.objects.filter(competencia=instance.competencia).first()

        if etapa4 and etapa4.usuarios_notificados and not etapa4.fecha_inicio:
            etapa4.fecha_inicio = timezone.now()
            etapa4.save()