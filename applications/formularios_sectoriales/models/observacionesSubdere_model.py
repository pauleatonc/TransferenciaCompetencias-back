from django.db import models

from applications.base.models import BaseModel
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.sectores_gubernamentales.models import SectorGubernamental
from django.utils import timezone


class ObservacionesSubdereFormularioSectorial(BaseModel):
    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='observaciones_sectoriales')
    observacion_paso1 = models.TextField(max_length=500, blank=True)
    observacion_paso2 = models.TextField(max_length=500, blank=True)
    observacion_paso3 = models.TextField(max_length=500, blank=True)
    observacion_paso4 = models.TextField(max_length=500, blank=True)
    observacion_paso5 = models.TextField(max_length=500, blank=True)

    observacion_enviada = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.observacion_enviada and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(ObservacionesSubdereFormularioSectorial, self).save(*args, **kwargs)

    def __str__(self):
        return f"Observación para {self.formulario_sectorial.sector.nombre}"