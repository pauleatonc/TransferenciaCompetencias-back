from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from applications.base.functions import validate_file_size_twenty
from applications.base.models import BaseModel
from applications.formularios_gores.models import FormularioGORE


class ObservacionesSubdereFormularioGORE(BaseModel):
    formulario_gore = models.OneToOneField(FormularioGORE, on_delete=models.CASCADE, related_name='observaciones_gore')
    observacion_paso1 = models.TextField(max_length=500, blank=True)
    observacion_paso2 = models.TextField(max_length=500, blank=True)
    observacion_paso3 = models.TextField(max_length=500, blank=True)
    documento = models.FileField(upload_to='formulario_gore',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Documento observación', blank=True, null=True)
    descripcion_documento = models.TextField(max_length=500, blank=True)

    observacion_enviada = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.observacion_enviada and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(ObservacionesSubdereFormularioGORE, self).save(*args, **kwargs)

    def __str__(self):
        return f"Observación para {self.formulario_gore.region.region}"