from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.conf import settings
#

from applications.base.models import BaseModel
from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental


class Competencia(BaseModel):
    ORIGEN = (
        ('OP', 'Oficio Presidencial'),
        ('SG', 'Solicitud GORE')
    )
    AMBITO = (
        ('AP', 'Fomento de las Actividades Productivas'),
        ('OT', 'Ordenamiento Territorial'),
        ('DSC', 'Desarrollo Social y Cultural')
    )
    ESTADO = (
        ('EP', 'En Proceso'),
        ('FIN', 'Cerrada'),
        ('SU', 'Sin usuarios')
    )

    nombre = models.CharField(max_length=200, unique=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='competencia_creada',
        verbose_name='Creado por'
    )
    sectores = models.ManyToManyField(
        SectorGubernamental,
        blank=False,
        verbose_name='Sectores'
    )
    ambito = models.CharField(max_length=5, choices=AMBITO, default='AP')
    regiones = models.ManyToManyField(
        Region,
        blank=False,
        verbose_name='Regiones'
    )
    origen = models.CharField(max_length=5, choices=ORIGEN, default='OP')
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=5, choices=ESTADO, default='SU')
    plazo_formulario_sectorial = models.IntegerField(
        validators=[
            MinValueValidator(15),
            MaxValueValidator(30)
        ],
        help_text="El plazo debe estar entre 15 y 30 días."
    )
    plazo_formulario_gore = models.IntegerField(
        validators=[
            MinValueValidator(15),
            MaxValueValidator(30)
        ],
        help_text="El plazo debe estar entre 15 y 30 días."
    )
    usuarios_subdere = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_subdere',
        blank=True,
        limit_choices_to={'groups__name': 'SUBDERE'}
    )
    usuarios_dipres = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_dipres',
        blank=True,
        limit_choices_to={'groups__name': 'DIPRES'}
    )
    usuarios_sectoriales = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_sectoriales',
        blank=True,
        limit_choices_to=Q(groups__name='Usuario Sectorial')
    )
    usuarios_gore = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_gore',
        blank=True,
        limit_choices_to=Q(groups__name='GORE')
    )


    class Meta:
        verbose_name = 'Competencia'
        verbose_name_plural = 'Competencias'



    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        creating = not bool(self.pk)  # Verificar si es una creación
        super().save(*args, **kwargs)  # Primero guardamos para obtener un ID

        # Ahora se pueden manejar las relaciones many-to-many
        if creating:
            if self.usuarios_subdere.filter(is_active=True).count() > 1:
                raise ValidationError("Solo puede haber un usuario SUBDERE activo.")
            if self.usuarios_dipres.filter(is_active=True).count() > 1:
                raise ValidationError("Solo puede haber un usuario DIPRES activo.")
            # ... otras validaciones many-to-many ...

        # Finalmente, asignar usuarios si es un nuevo objeto
        if creating and self.creado_por:
            self.usuarios_subdere.add(self.creado_por)


# Receptor de señal para la validación de usuarios sectoriales y GORE
@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
def validar_usuarios_sector(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        for pk in pk_set:
            usuario = settings.AUTH_USER_MODEL.objects.get(pk=pk)
            if usuario.sector not in instance.sectores.all():
                raise ValidationError(f"El usuario {usuario.username} no pertenece a los sectores asignados a esta competencia.")

@receiver(m2m_changed, sender=Competencia.usuarios_gore.through)
def validar_usuarios_gore(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        for pk in pk_set:
            usuario = settings.AUTH_USER_MODEL.objects.get(pk=pk)
            if usuario.region not in instance.regiones.all():
                raise ValidationError(f"El usuario {usuario.username} no pertenece a las regiones asignadas a esta competencia.")