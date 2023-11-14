from django.db import models
from django.utils import timezone

#
from .base import EtapaBase


class Etapa1(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Inicio de Transferencia de Competencia'

    competencia_creada = models.BooleanField(default=True)

    @property
    def estado_competencia_creada(self):
        return 'Finalizada' if self.competencia_creada else 'No Finalizada'

    @property
    def usuario_sectorial_vinculado(self):
        return self.competencia.usuarios_sectoriales.exists()

    def save(self, *args, **kwargs):
        if self.usuario_sectorial_vinculado and not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()  # Asignar la fecha de inicio al momento de asignar usuarios
            self.plazo_dias = self.competencia.plazo_formulario_sectorial
            self.aprobada = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"