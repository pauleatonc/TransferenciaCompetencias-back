from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.db import models
from rest_framework.exceptions import ValidationError

#
from .functions import validar_rut
from .managers import UserManager
# apps de terceros
from simple_history.models import HistoricalRecords
#
from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.competencias.models import Competencia


class User(AbstractBaseUser, PermissionsMixin):

    PERFILES = [
        ('SUBDERE', 'SUBDERE'),
        ('DIPRES', 'DIPRES'),
        ('Usuario Sectorial', 'Usuario Sectorial'),
        ('GORE', 'GORE'),
        ('Usuario Observador', 'Usuario Observador'),
    ]

    rut = models.CharField(max_length=15, validators=[validar_rut], unique=True)
    nombre_completo = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True)
    email = models.TextField(max_length=100, blank=True, null=True)
    perfil = models.CharField(max_length=20, choices=PERFILES, default='Usuario Observador')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    #Seteando el nombre de usuario al RUT
    USERNAME_FIELD = 'rut'

    is_staff = models.BooleanField('Usuario administrador', default=False)
    is_active = models.BooleanField(default=True)

    historical_date = HistoricalRecords(user_model='users.User', inherit=True)

    #Campos requeridos
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def clean(self):
        super().clean()
        # Validar que el sector y la región son obligatorios si el perfil es Sectorial o GORE
        if self.perfil == 'Usuario Sectorial' and not self.sector:
            raise ValidationError({'sector': 'El campo sector es obligatorio para el perfil Usuario Sectorial.'})
        if self.perfil == 'GORE' and not self.region:
            raise ValidationError({'region': 'El campo región es obligatorio para el perfil GORE.'})

    def save(self, *args, **kwargs):
        # Formatear el RUT antes de guardar
        rut_formateado = validar_rut(self.rut)
        self.rut = rut_formateado
        # Llamada a la implementación de save() de la superclase
        super().save(*args, **kwargs)
        # Asignar grupos después de guardar el usuario
        self.groups.clear()  # Eliminar todos los grupos existentes primero
        self.groups.add(Group.objects.get(name=self.perfil))

    class Meta:
        verbose_name= 'Usuario'
        verbose_name_plural= 'Usuarios'