from rest_framework import permissions
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission


def is_SUBDERE_or_superuser(user: User) -> bool:
    return user.groups.filter(name='SUBDERE').exists() or user.is_superuser

def is_DIPRES(user: User) -> bool:
    return user.groups.filter(name='DIPRES').exists() or user.is_superuser

def is_Sectorial(user: User) -> bool:
    return user.groups.filter(name='Usuario Sectorial').exists() or user.is_superuser

def is_GORE(user: User) -> bool:
    return user.groups.filter(name='GORE').exists() or user.is_superuser

def is_Observador(user: User) -> bool:
    return user.groups.filter(name='Usuario Observador').exists() or user.is_superuser


class CanEditUser(permissions.BasePermission):
    """
    Permiso personalizado para verificar quién puede editar a quién.
    """

    def has_object_permission(self, request, view, obj):
        # Los usuarios pueden editar su propio perfil
        if request.user == obj:
            return True

        # Superusuarios pueden editar a todos, excepto a otros superusuarios
        if request.user.is_superuser:
            return not obj.is_superuser

        # Los usuarios SUBDERE pueden editar a todos, excepto superusuarios y a otros usuarios SUBDERE
        if request.user.groups.filter(name="SUBDERE").exists():
            return not obj.is_superuser and not obj.groups.filter(name="SUBDERE").exists()

        # En cualquier otro caso, no se permite la edición
        return False