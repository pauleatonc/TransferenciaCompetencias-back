from django.db import models
from applications.competencias.models import Competencia
from applications.regioncomuna.models import Region


class FormularioGORE(models.Model):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='formularios_gores')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {self.region.region}"
