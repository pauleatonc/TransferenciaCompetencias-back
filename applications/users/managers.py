from django.db import models
#
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager, models.Manager):

    def _create_user(self, rut, password, is_staff, is_superuser, is_active, **extra_fields):
        user = self.model(
            rut=rut,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_user(self, rut, password=None, **extra_fields):
        return self._create_user(rut, password, False, False, True, **extra_fields)

    def create_superuser(self, rut, password=None, **extra_fields):
        return self._create_user(rut, password, True, True, True, **extra_fields)

    def cod_validation(self, id_user, cod_registro):
        if self.filter(id=id_user, codregistro=cod_registro).exists():
            return True
        else:
            return False