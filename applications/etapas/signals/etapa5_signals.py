from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from django.utils import timezone

from applications.etapas.models import Etapa4, Etapa5


@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa5_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if isinstance(instance, Competencia):
            etapa5 = Etapa5.objects.filter(competencia=instance).first()
            if etapa5:
                etapa5.usuario_notificado = instance.usuarios_dipres.exists()
                etapa5.save()


@receiver(post_save, sender=Etapa5)
def verificar_y_aprobar_etapa5(sender, instance, **kwargs):
    # Verificar si ya se está procesando para evitar recursión
    if getattr(instance, '_no_recurse', False):
        return

    if instance.observacion_minuta_gore_enviada:
        instance.aprobada = True
        # Establecer la bandera antes de guardar para evitar recursión
        setattr(instance, '_no_recurse', True)
        instance.save()
        # Quitar la bandera después de guardar
        delattr(instance, '_no_recurse')
