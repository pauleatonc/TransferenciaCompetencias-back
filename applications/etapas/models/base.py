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
    fecha_inicio = models.DateTimeField(null=True, blank=True)
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
        elif self.segundos_restantes() < 0:
            return 'atrasada'
        elif self.aprobada:
            return 'finalizada'
        elif self.enviada:
            return 'en_revision'
        else:
            return 'en_estudio'

    @property
    def tiempo_restante(self):
        """
        Calcula el tiempo restante hasta el final del plazo.
        Si la fecha de inicio no está establecida o el plazo no está definido, retorna 0 para cada unidad de tiempo.
        """
        if self.fecha_inicio and self.plazo_dias is not None:
            tiempo_actual = timezone.now()
            delta = tiempo_actual - self.fecha_inicio
            segundos_restantes = max(self.plazo_dias * 24 * 3600 - delta.total_seconds(), 0)

            # Convertir segundos restantes a días, horas y minutos
            dias_restantes = segundos_restantes // (24 * 3600)
            horas_restantes = (segundos_restantes % (24 * 3600)) // 3600
            minutos_restantes = (segundos_restantes % 3600) // 60

            return {
                'dias': int(dias_restantes),
                'horas': int(horas_restantes),
                'minutos': int(minutos_restantes),
            }
        return {'dias': 0, 'horas': 0, 'minutos': 0}


    def segundos_restantes(self):
        if self.fecha_inicio and self.plazo_dias is not None:
            tiempo_actual = timezone.now()
            delta = tiempo_actual - self.fecha_inicio
            return max(self.plazo_dias * 24 * 3600 - delta.total_seconds(), 0)
        return 0


    def save(self, *args, **kwargs):
        # Actualiza el estado antes de guardar
        self.estado = self.actualizar_estado()
        super().save(*args, **kwargs)