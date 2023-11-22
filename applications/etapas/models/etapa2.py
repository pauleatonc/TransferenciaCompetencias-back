from django.core.validators import FileExtensionValidator
from django.db import models

#
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
    comentario_observacion_etapa2 = models.TextField(max_length=500, blank=True)
    archivo_observacion_etapa2 = models.FileField(upload_to='observaciones_etapa2',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               validate_file_size_twenty],
                                           verbose_name='Archivo Observación Etapa 2', blank=True, null=True)
    observacion_etapa2_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 2'
        verbose_name_plural = "Etapas 2"


    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"