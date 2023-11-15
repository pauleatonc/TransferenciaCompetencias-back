from django.db import models
from applications.competencias.models import Competencia
from applications.sectores_gubernamentales.models import SectorGubernamental


class FormularioSectorial(models.Model):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='formularios_sectoriales')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {self.sector.nombre}"
