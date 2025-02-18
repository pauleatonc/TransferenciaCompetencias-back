from django.db import models

#
from applications.etapas.models import EtapaBase


class Etapa2(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Levantamiento de antecedentes sectoriales'

    """ Campos subetapa 2"""
    usuarios_notificados = models.BooleanField(default=False)
    formulario_completo = models.BooleanField(default=False)
    observaciones_completas = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 2'
        verbose_name_plural = "Etapas 2"


    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"
