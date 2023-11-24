from django.core.validators import FileExtensionValidator
from django.db import models

#
from applications.base.functions import validate_file_size_twenty
from applications.etapas.models import EtapaBase
from applications.formularios_sectoriales.models import FormularioSectorial


class Etapa2(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Levantamiento de antecedentes sectoriales'

    """ Campos subetapa 2"""
    usuarios_notificados = models.BooleanField(default=False)
    formulario_completo = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 2'
        verbose_name_plural = "Etapas 2"


    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"


class ObservacionSectorial(models.Model):
    formulario_sectorial = models.OneToOneField(
        FormularioSectorial,
        on_delete=models.CASCADE,
        related_name='observacion'
    )
    comentario = models.TextField(max_length=500, blank=True)
    archivo = models.FileField(
        upload_to='observaciones_formularios',
        validators=[
            FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'),
            validate_file_size_twenty
        ],
        verbose_name='Archivo de Observación',
        blank=True,
        null=True
    )
    observacion_enviada = models.BooleanField(default=False)

    def __str__(self):
        return f"Observación para {self.formulario_sectorial.sector.nombre}"