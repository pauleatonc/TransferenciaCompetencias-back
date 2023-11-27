from django.db import models
#
from applications.etapas.models import EtapaBase


class Etapa4(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Levantamiento de antecedentes GORE'

    """ Campos subetapa 4"""
    usuarios_notificados = models.BooleanField(default=False)
    formulario_completo = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Etapa 4'
        verbose_name_plural = "Etapas 4"

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"