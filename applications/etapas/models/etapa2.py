from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import Q
#
from applications.competencias.models import Competencia
from applications.base.functions import validate_file_size_twenty
from applications.etapas.models import EtapaBase


class Etapa2(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Levantamiento de antecedentes sectoriales'

    """ Campos subetapa 2"""
    usuarios_notificados = models.BooleanField(default=False)
    formulario_completo = models.BooleanField(default=False)

    """ Campos Revisión"""
    comentario_observacion = models.TextField(max_length=500, blank=True)
    archivo_observacion = models.FileField(upload_to='observaciones',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               validate_file_size_twenty],
                                           verbose_name='Archivo Observación', blank=True, null=True)
    observacion_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 2'
        verbose_name_plural = "Etapas 2"


    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"