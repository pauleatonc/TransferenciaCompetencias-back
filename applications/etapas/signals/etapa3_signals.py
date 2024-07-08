from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa3


@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa3_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if isinstance(instance, Competencia):
            etapa3 = Etapa3.objects.filter(competencia=instance).first()
            if etapa3:
                etapa3.usuario_notificado = instance.usuarios_dipres.exists()
                etapa3.save()

@receiver(post_save, sender=Etapa3)
def verificar_y_aprobar_etapa3(sender, instance, **kwargs):
    # Verificar si ya se está procesando para evitar recursión
    if getattr(instance, '_no_recurse', False):
        return

    if instance.observacion_minuta_sectorial_enviada:
        instance.aprobada = True
        # Establecer la bandera antes de guardar para evitar recursión
        setattr(instance, '_no_recurse', True)
        instance.save()
        # Quitar la bandera después de guardar
        delattr(instance, '_no_recurse')
