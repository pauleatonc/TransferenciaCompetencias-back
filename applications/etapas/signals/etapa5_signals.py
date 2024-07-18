from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa5


@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa5_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if isinstance(instance, Competencia):
            etapa5 = Etapa5.objects.filter(competencia=instance).first()
            if etapa5:
                etapa5.usuario_notificado = instance.usuarios_dipres.exists()
                etapa5.save()
