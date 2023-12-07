from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

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