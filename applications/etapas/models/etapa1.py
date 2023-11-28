from django.db import models
#
from .base import EtapaBase


class Etapa1(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Inicio de Transferencia de Competencia'

    competencia_creada = models.BooleanField(default=True)
    usuarios_vinculados = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"