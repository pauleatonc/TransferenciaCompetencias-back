from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from applications.competencias.models import Competencia


@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
def actualizar_etapa1_al_modificar_usuarios_sectoriales(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        etapa1 = instance.etapa1

        if etapa1:
            todos_los_usuarios_vinculados = True
            for sector in instance.sectores.all():
                if not instance.usuarios_sectoriales.filter(sector=sector).exists():
                    todos_los_usuarios_vinculados = False
                    break

            if todos_los_usuarios_vinculados:
                # Todos los usuarios están vinculados
                etapa1.usuarios_vinculados = True
                etapa1.aprobada = True
                etapa1.competencia_creada = True
                if not etapa1.fecha_inicio:
                    etapa1.fecha_inicio = timezone.now()
                etapa1.save()

                if instance.estado != 'EP':
                    instance.estado = 'EP'
                    instance.save()
            else:
                # No todos los usuarios están vinculados
                etapa1.usuarios_vinculados = False
                etapa1.aprobada = False
                etapa1.competencia_creada = False
                etapa1.save()

                if instance.estado != 'SU':
                    instance.estado = 'SU'
                    instance.save()
