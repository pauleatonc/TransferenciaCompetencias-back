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
    def estado_usuarios_vinculados(self):
        usuarios_vinculados = all(
            self.competencia.usuarios_sectoriales.filter(sector=sector).exists()
            for sector in self.competencia.sectores.all()
        )
        self.usuarios_vinculados = usuarios_vinculados
        return 'finalizada' if usuarios_vinculados else 'pendiente'

    def save(self, *args, **kwargs):
        # Llama a estado_usuarios_vinculados para actualizar usuarios_vinculados
        self.estado_usuarios_vinculados

        # Verificar si ya tiene asignados todos los usuarios de los sectores requeridos
        self.usuarios_vinculados = all(
            self.competencia.usuarios_sectoriales.filter(sector=sector).exists()
            for sector in self.competencia.sectores.all()
        )

        # Si todos los sectores tienen al menos un usuario y aún no se ha establecido fecha_inicio
        if self.usuarios_vinculados:
            if not self.fecha_inicio:
                # Establecer la fecha de inicio solo si no estaba previamente establecida
                self.fecha_inicio = timezone.now()
            # Independientemente de la fecha de inicio, la etapa se considera aprobada
            self.aprobada = True
            self.competencia.estado = 'EP'
        else:
            # Si no están todos los usuarios, la etapa no está aprobada
            self.aprobada = False
            self.competencia.estado = 'SU'

        # Actualizar la propiedad competencia_creada
        self.competencia_creada = True

        # Guardar los cambios en la instancia actual
        super().save(*args, **kwargs)

        # Guardar el objeto competencia si ha habido cambios en su estado
        if self.competencia_id and self.competencia.estado in ['EP', 'SU']:
            self.competencia.save()

    def __str__(self):
        return f"{self.nombre_etapa} para {self.competencia.nombre}"