from django.core.validators import FileExtensionValidator
from django.db import models

#
from applications.base.functions import validate_file_size_twenty
from applications.etapas.models import EtapaBase


class Etapa5(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Complemento y validación de DIPRES'

    """ Campos subetapa 5"""
    usuario_notificado = models.BooleanField(default=False)

    """ Campos DIPRES etapa 5"""
    archivo_minuta_etapa5 = models.FileField(upload_to='minutas_dipres_etapa5',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               validate_file_size_twenty],
                                           verbose_name='Archivo minuta DIPRES Etapa 5', blank=True, null=True)
    minuta_etapa5_enviada = models.BooleanField(default=False)

    """ Campos Revisión SUBDERE etapa 5"""
    comentario_minuta_gore = models.TextField(max_length=500, blank=True)

    observacion_minuta_gore_enviada = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Etapa 5'
        verbose_name_plural = "Etapas 5"

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"