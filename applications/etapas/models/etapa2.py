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
from applications.base.functions import TWENTY_SIZE_LIMIT
from applications.etapas.models import EtapaBase


class Etapa2(EtapaBase):
    """ Campos subetapa 2"""
    usuarios_notificados = models.BooleanField(default=False)
    formulario_completo = models.BooleanField(default=False)

    """ Campos Revisión"""
    comentario_observacion = models.TextField(max_length=500, blank=True)
    archivo_observacion = models.FileField(upload_to='observaciones',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               TWENTY_SIZE_LIMIT],
                                           verbose_name='Archivo Observación')
    observacion_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 2'
        verbose_name_plural = "Etapas 2"

