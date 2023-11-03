from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
#
from django.db import models
from .functions import validar_rut
from .managers import UserManager
from applications.regioncomuna.models import Comuna
# apps de terceros
from simple_history.models import HistoricalRecords


class User(AbstractBaseUser, PermissionsMixin):

    rut = models.CharField(max_length=15, validators=[validar_rut], unique=True)
    nombre_completo = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True)
    email = models.TextField(max_length=100, blank=True, null=True)

    #Seteando el nombre de usuario al RUT
    USERNAME_FIELD = 'rut'

    is_staff = models.BooleanField('Usuario administrador', default=False)
    is_active = models.BooleanField(default=True)

    historical_date = HistoricalRecords(user_model='users.User', inherit=True)

    #Campos requeridos
    REQUIRED_FIELDS = ['email']

    objects = UserManager()


    def save(self, *args, **kwargs):
        # Formatear el RUT antes de guardar
        rut_formateado = validar_rut(self.rut)
        self.rut = rut_formateado
        super().save(*args, **kwargs)

    class Meta:
        verbose_name= 'Usuario'
        verbose_name_plural= 'Usuarios'