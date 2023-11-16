from django.db import models
from django.utils import timezone

#
from .base import EtapaBase


class Etapa1(EtapaBase):
    @property
    def nombre_etapa(self):
        return 'Inicio de Transferencia de Competencia'

    competencia_creada = models.BooleanField(default=True)
    usuarios_vinculados = models.BooleanField(default=False)

    @property
    def estado_competencia_creada(self):
        # Asumimos que la competencia está creada si se ha creado la instancia Etapa1
        competencia_creada = self.competencia_creada

        return 'Finalizada' if competencia_creada else 'No Finalizada'

    @property
    def estado_usuarios_vinculados(self):
        # Inicializar como True. Asumimos que todos los sectores tienen usuarios asignados.
        usuarios_vinculados = True

        # Verificar que cada sector de la competencia tenga al menos un usuario asignado
        for sector in self.competencia.sectores.all():
            if not self.competencia.usuarios_sectoriales.filter(sector=sector).exists():
                usuarios_vinculados = False
                break

        # Devolver 'Finalizada' si cada sector tiene al menos un usuario asignado
        return 'Finalizada' if usuarios_vinculados else 'Usuarios pendientes'

    def save(self, *args, **kwargs):
        # Actualizar la propiedad competencia_creada y usuarios_vinculados antes de guardar
        self.competencia_creada = True
        self.usuarios_vinculados = self.estado_usuarios_vinculados == 'Finalizada'

        # Verificar que todos los sectores tienen al menos un usuario asignado
        if self.usuarios_vinculados and not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()
            self.plazo_dias = self.competencia.plazo_formulario_sectorial
            self.aprobada = True
            self.competencia.estado = 'EP'
        else:
            self.aprobada = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"