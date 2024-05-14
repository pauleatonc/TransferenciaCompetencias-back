from django.core.validators import FileExtensionValidator
from django.db import models

from applications.base.functions import validate_file_size_twenty
from applications.competencias.models import Competencia
from applications.regioncomuna.models import Region
from django.utils import timezone
from applications.base.models import BaseModel


class FormularioGORE(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='formulario_gore')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)
    intento_envio = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    antecedente_adicional_gore = models.FileField(upload_to='formulario_gore',
                                                       validators=[
                                                           FileExtensionValidator(
                                                               ['pdf'], message='Solo se permiten archivos PDF.'),
                                                           validate_file_size_twenty],
                                                       verbose_name='Antecedentes adicionales formulario GORE',
                                                       blank=True, null=True)
    descripcion_antecedente = models.TextField(blank=True, null=True, max_length=500)

    def save(self, *args, **kwargs):
        if self.formulario_enviado and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(FormularioGORE, self).save(*args, **kwargs)

    def delete_file(self):
        if self.antecedente_adicional_gore:
            self.antecedente_adicional_gore.delete(save=False)
            self.antecedente_adicional_gore = None
            self.save()

    def __str__(self):
        return f"{self.nombre} - {self.region.region}"


class PasoBase(BaseModel):

    @property
    def completado(self):
        return self.campos_obligatorios_completados

    @property
    def campos_obligatorios_completados(self):
        completados, total_campos = self.avance_numerico()
        return completados == total_campos

    @property
    def estado_stepper(self):
        if self.campos_obligatorios_completados:
            return 'done'
        elif self.formulario_gore.intento_envio and not self.campos_obligatorios_completados:
            return 'warning'
        else:
            return 'default'

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} - {self.formulario_gore.nombre}"
