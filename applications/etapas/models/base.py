from django.db import models
from django.utils import timezone

#
from applications.competencias.models import Competencia
from applications.base.models import BaseModel


class EtapaBase(BaseModel):
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
    tiempo_transcurrido_registrado = models.IntegerField(default=0)
    ultima_finalizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def nombre_etapa(self):
        raise NotImplementedError("Subclases deben implementar este método.")

    def actualizar_estado(self):
        tiempo_transcurrido = self.calcular_tiempo_transcurrido()
        if not self.fecha_inicio:
            return 'no_iniciada'
        elif self.aprobada:
            return 'finalizada'
        elif self.enviada:
            return 'en_revision'
        elif tiempo_transcurrido['dias'] > self.plazo_dias:
            return 'atrasada'
        else:
            return 'en_estudio'

    def segundos_restantes(self):
        if self.fecha_inicio and self.plazo_dias is not None:
            tiempo_actual = timezone.now()
            delta = tiempo_actual - self.fecha_inicio
            return max(self.plazo_dias * 24 * 3600 - delta.total_seconds(), 0)
        return 0

    def calcular_tiempo_transcurrido(self):
        """
        Calcula el tiempo transcurrido en segundos desde fecha_inicio hasta ahora.
        """
        if self.fecha_inicio:
            tiempo_actual = timezone.now()
            delta = tiempo_actual - self.fecha_inicio
            total_seconds = int(delta.total_seconds())
            dias = total_seconds // (24 * 3600)
            horas = (total_seconds % (24 * 3600)) // 3600
            minutos = (total_seconds % 3600) // 60
            return {'dias': dias, 'horas': horas, 'minutos': minutos}
        return {'dias': 0, 'horas': 0, 'minutos': 0}

    def save(self, *args, **kwargs):
        # Obtener el estado anterior y el estado de 'enviada' si el objeto ya existe
        estado_anterior = None
        enviada_anterior = None
        if self.pk:
            instancia_concreta = self.__class__.objects.get(pk=self.pk)
            estado_anterior = instancia_concreta.estado
            enviada_anterior = instancia_concreta.enviada

        # Actualizar el estado antes de guardar
        self.estado = self.actualizar_estado()

        # Guardar los cambios para obtener el estado actualizado en la base de datos
        super().save(*args, **kwargs)

        # Si 'enviada' cambia de False a True
        if self.enviada and not enviada_anterior:
            tiempo_transcurrido = self.calcular_tiempo_transcurrido()
            self.tiempo_transcurrido_registrado = tiempo_transcurrido['dias'] * 24 * 3600 + tiempo_transcurrido['horas'] * 3600 + tiempo_transcurrido['minutos'] * 60
            # Actualizar el campo sin disparar nuevamente el método save
            EtapaBase.objects.filter(pk=self.pk).update(tiempo_transcurrido_registrado=self.tiempo_transcurrido_registrado)

        # Si cambia a 'finalizada' desde cualquier otro estado (mantiene la lógica existente)
        if self.estado == 'finalizada' and estado_anterior != 'finalizada':
            # Actualiza 'ultima_finalizacion' con la fecha y hora actual
            self.ultima_finalizacion = timezone.now()
            super().save(update_fields=['ultima_finalizacion'])