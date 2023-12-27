from django.db import models

from applications.base.models import BaseModel
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.sectores_gubernamentales.models import SectorGubernamental
from django.utils import timezone


class ObservacionesSubdereFormularioSectorial(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='observaciones_sectoriales')
    observacion_paso1 = models.TextField(max_length=500, blank=True)
    observacion_paso2 = models.TextField(max_length=500, blank=True)
    observacion_paso3 = models.TextField(max_length=500, blank=True)
    observacion_paso4 = models.TextField(max_length=500, blank=True)
    observacion_paso5 = models.TextField(max_length=500, blank=True)
