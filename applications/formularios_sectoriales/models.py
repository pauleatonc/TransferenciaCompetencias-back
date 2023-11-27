from django.db import models
from applications.competencias.models import Competencia
from applications.sectores_gubernamentales.models import SectorGubernamental
from django.utils import timezone


class FormularioSectorial(models.Model):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='formularios_sectoriales')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.formulario_enviado and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(FormularioSectorial, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.sector.nombre}"
