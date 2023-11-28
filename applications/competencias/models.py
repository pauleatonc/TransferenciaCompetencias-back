from django.db import models

from django.db.models import Q
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta

from django.utils import timezone

from applications.base.functions import validate_file_size_twenty, validate_file_size_five
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
    oficio_origen = models.FileField(upload_to='oficios_competencias',
                                             validators=[
                                                 FileExtensionValidator(
                                                     ['pdf'], message='Solo se permiten archivos PDF.'),
                                                 validate_file_size_twenty],
                                             verbose_name='Oficio Origen Competencia', blank=True, null=True)

    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
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


    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()


    def tiempo_transcurrido(self):
        """
        Calcula el tiempo transcurrido desde fecha_inicio hasta fecha_fin.
        Si fecha_fin no está asignada, usa el tiempo actual.
        Devuelve un diccionario con los días, horas y minutos transcurridos.
        """
        if not self.fecha_inicio:
            return {"dias": None, "horas": None, "minutos": None}

        fecha_fin = self.fecha_fin if self.fecha_fin else timezone.now()

        diferencia = fecha_fin - self.fecha_inicio
        dias = diferencia.days
        horas = diferencia.seconds // 3600
        minutos = (diferencia.seconds % 3600) // 60

        return {"dias": dias, "horas": horas, "minutos": minutos}


class DocumentosComplementarios(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    nombre_documento = models.CharField(max_length=100, unique=True)
    documento = models.FileField(upload_to='documentos_competencias',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               validate_file_size_five],
                                           verbose_name='Documentos complementarios Competencia', blank=True, null=True)
