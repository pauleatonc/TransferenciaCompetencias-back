from django.db import models
from django.utils import timezone

#
from applications.competencias.models import Competencia


class EtapaBase(models.Model):
    ESTADOS = (
        ('finalizada', 'Finalizada'),
        ('en_estudio', 'En Estudio'),
        ('no_iniciada', 'Aún no puede comenzar'),
        ('en_revision', 'En revisión'),
        ('atrasada', 'Atrasada'),
    )

    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='no_iniciada')
    fecha_inicio = models.DateField(null=True, blank=True)
    plazo_dias = models.IntegerField(null=True, blank=True)
    enviada = models.BooleanField(default=False)
    aprobada = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @property
    def nombre_etapa(self):
        raise NotImplementedError("Subclases deben implementar este método.")

    def actualizar_estado(self):
        if not self.fecha_inicio:
            return 'no_iniciada'
        elif self.tiempo_restante < 0:
            return 'atrasada'
        elif self.aprobada:
            return 'finalizada'
        elif self.enviada:
            return 'en_revision'
        else:
            return 'en_estudio'

    @property
    def tiempo_restante(self):
        if self.fecha_inicio:
            delta = timezone.now().date() - self.fecha_inicio
            return max(self.plazo_dias - delta.days, 0)
        return self.plazo_dias

    def save(self, *args, **kwargs):
        # Actualiza el estado antes de guardar
        self.estado = self.actualizar_estado()
        super().save(*args, **kwargs)