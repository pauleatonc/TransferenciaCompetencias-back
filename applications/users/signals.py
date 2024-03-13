from django.contrib.auth.models import Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import User
from ..competencias.models import Competencia


@receiver(post_save, sender=User)
def update_user_group(sender, instance, created, **kwargs):
    if not created:  # Solo actuar si el usuario está siendo actualizado, no creado
        user_groups = instance.groups.all()
        current_group_names = set(group.name for group in user_groups)
        new_group_name = instance.perfil

        # Verifica si el grupo actual es diferente del perfil y actualiza si es necesario
        if new_group_name not in current_group_names:
            # Limpiar los grupos existentes y asignar el nuevo grupo basado en el perfil
            instance.groups.clear()
            new_group, created = Group.objects.get_or_create(name=new_group_name)
            instance.groups.add(new_group)


@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
def validar_usuarios_sectoriales(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        competencia_sectores = instance.sectores.all()
        for user_id in pk_set:
            user = User.objects.get(id=user_id)
            if user.sector not in competencia_sectores:
                raise ValueError("Los usuarios sectoriales deben compartir el mismo sector de la competencia.")


@receiver(m2m_changed, sender=Competencia.usuarios_gore.through)
def validar_usuarios_gore(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        competencia_regiones = instance.regiones.all()
        for user_id in pk_set:
            user = User.objects.get(id=user_id)
            if user.region not in competencia_regiones:
                raise ValueError("Los usuarios GORE deben compartir la misma región de la competencia.")
