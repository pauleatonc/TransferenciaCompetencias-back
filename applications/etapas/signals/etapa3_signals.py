from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from django.utils import timezone

from applications.etapas.models import Etapa3
from applications.formularios_gores.models import FormularioGORE
from applications.regioncomuna.models import Region


@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa3_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if isinstance(instance, Competencia):
            etapa3 = Etapa3.objects.filter(competencia=instance).first()
            if etapa3:
                etapa3.usuario_notificado = instance.usuarios_dipres.exists()
                etapa3.save()

