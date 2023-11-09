from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
#
from django.conf import settings
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
    ambito = models.CharField(max_length=5, choices=ORIGEN, default='AP')
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


    def total_etapas(self):
        return self.etapas.count()

    def etapas_finalizadas(self):
        return self.etapas.filter(estado='finalizada').count()

    @property
    def porcentaje_avance(self):
        total = self.total_etapas()
        finalizadas = self.etapas_finalizadas()
        return (finalizadas / total * 100) if total > 0 else 0

    def clean(self):
        # Validación para asegurarse de que solo haya un usuario SUBDERE y DIPRES activos
        if self.usuarios_subdere.filter(is_active=True).count() > 1:
            raise ValidationError("Solo puede haber un usuario SUBDERE activo.")
        if self.usuarios_dipres.filter(is_active=True).count() > 1:
            raise ValidationError("Solo puede haber un usuario DIPRES activo.")
        # Aquí puedes agregar las validaciones para usuarios_sectoriales y usuarios_gore
        super().clean()

    def save(self, *args, **kwargs):
        if not self.pk:  # Indica que la instancia es nueva
            # Asume que el usuario que crea la competencia es un usuario SUBDERE
            self.usuarios_subdere.add(self.creado_por)  # 'creado_por' debe ser el usuario SUBDERE que crea la competencia
        self.full_clean()
        super().save(*args, **kwargs)


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