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

        return 'finalizada' if competencia_creada else 'pendiente'

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
        return 'finalizada' if usuarios_vinculados else 'pendiente'

    def save(self, *args, **kwargs):
        # Verificar si ya tiene asignados todos los usuarios de los sectores requeridos
        sectores_asignados_completamente = all(
            self.competencia.usuarios_sectoriales.filter(sector=sector).exists()
            for sector in self.competencia.sectores.all()
        )

        # Si todos los sectores tienen al menos un usuario y aún no se ha establecido fecha_inicio
        if sectores_asignados_completamente:
            if not self.fecha_inicio:
                # Establecer la fecha de inicio solo si no estaba previamente establecida
                self.fecha_inicio = timezone.now()
            # Independientemente de la fecha de inicio, si todos los usuarios están asignados, la etapa está aprobada
            self.aprobada = True
            self.competencia.estado = 'EP'
        else:
            # Si no están todos los usuarios, la etapa no está aprobada y la competencia está 'Sin usuarios'
            self.aprobada = False
            self.competencia.estado = 'SU'

        # Actualizar la propiedad competencia_creada y usuarios_vinculados antes de guardar
        self.competencia_creada = True
        self.usuarios_vinculados = sectores_asignados_completamente

        # Guardar el objeto competencia si ha habido cambios en su estado
        if self.competencia_id and self.competencia.estado in ['EP', 'SU']:
            self.competencia.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"