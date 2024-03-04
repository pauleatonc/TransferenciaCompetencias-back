from django.db import models
from applications.competencias.models import Competencia
from applications.regioncomuna.models import Region
from django.utils import timezone
from applications.base.models import BaseModel


class FormularioGORE(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='formulario_gore')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.formulario_enviado and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(FormularioGORE, self).save(*args, **kwargs)

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
