from django.core.validators import FileExtensionValidator
from django.db import models

#
from applications.base.functions import validate_file_size_twenty
from applications.etapas.models import EtapaBase


class Etapa3(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Complemento y validación de DIPRES'

    """ Campos subetapa 3"""
    usuario_notificado = models.BooleanField(default=False)
    omitir_etapa = models.BooleanField(default=False)

    """ Campos DIPRES etapa 3"""
    comentario_minuta_etapa3 = models.TextField(max_length=500, blank=True)
    archivo_minuta_etapa3 = models.FileField(upload_to='minutas_dipres_etapa3',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               validate_file_size_twenty],
                                           verbose_name='Archivo minuta DIPRES Etapa 3', blank=True, null=True)
    minuta_etapa3_enviada = models.BooleanField(default=False)

    """ Campos Revisión SUBDERE etapa 3"""
    comentario_minuta_sectorial = models.TextField(max_length=500, blank=True)
    archivo_observacion_minuta_sectorial = models.FileField(
        upload_to='observaciones_formularios_etapa3',
        validators=[
            FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'),
            validate_file_size_twenty
        ],
        verbose_name='Archivo de Observación',
        blank=True,
        null=True
    )
    observacion_minuta_sectorial_enviada = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Etapa 3'
        verbose_name_plural = "Etapas 3"

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"

