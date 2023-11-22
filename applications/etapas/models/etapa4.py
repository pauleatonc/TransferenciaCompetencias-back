from django.core.validators import FileExtensionValidator
from django.db import models

#
from applications.base.functions import validate_file_size_twenty
from applications.etapas.models import EtapaBase


class Etapa4(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Levantamiento de antecedentes GORE'

    """ Campos subetapa 4"""
    usuarios_notificados = models.BooleanField(default=False)
    formulario_completo = models.BooleanField(default=False)

    """ Campos Revisión"""
    comentario_observacion_etapa4 = models.TextField(max_length=500, blank=True)
    archivo_observacion_etapa4 = models.FileField(upload_to='observaciones_etapa4',
                                           validators=[
                                               FileExtensionValidator(
                                                   ['pdf'], message='Solo se permiten archivos PDF.'),
                                               validate_file_size_twenty],
                                           verbose_name='Archivo Observación Etapa 4', blank=True, null=True)
    observacion_etapa4_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 4'
        verbose_name_plural = "Etapas 4"


    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"