from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from applications.base.functions import validate_file_size_twenty
#
from applications.competencias.models import Competencia
from applications.base.models import BaseModel


class EtapaBase(BaseModel):
    ESTADOS = (
        ('finalizada', 'Finalizada'),
        ('en_estudio', 'En Estudio'),
        ('no_iniciada', 'Aún no puede comenzar'),
        ('en_revision', 'En revisión SUBDERE'),
        ('atrasada', 'Atrasada'),
        ('omitida', 'Omitida')
    )

    competencia = models.OneToOneField(Competencia, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='no_iniciada')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    plazo_dias = models.IntegerField(null=True, blank=True)
    enviada = models.BooleanField(default=False)
    aprobada = models.BooleanField(default=False)
    omitida = models.BooleanField(default=None, null=True, blank=True)
    tiempo_transcurrido_registrado = models.IntegerField(default=0)
    ultima_finalizacion = models.DateTimeField(null=True, blank=True)
    oficio_origen = models.FileField(upload_to='oficios_competencias',
                                     validators=[
                                         FileExtensionValidator(
                                             ['pdf'], message='Solo se permiten archivos PDF.'),
                                         validate_file_size_twenty],
                                     verbose_name='Oficio inicio etapa', blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def nombre_etapa(self):
        raise NotImplementedError("Subclases deben implementar este método.")

    def actualizar_estado(self):
        if not self.fecha_inicio:
            return 'no_iniciada'
        elif self.omitida:
            return 'omitida'
        elif self.aprobada:
            return 'finalizada'
        elif self.enviada:
            return 'en_revision'
        else:
            # Solo considerar el plazo si plazo_dias está definido
            if self.plazo_dias is not None:
                tiempo_transcurrido = self.calcular_tiempo_transcurrido()
                if tiempo_transcurrido['dias'] > self.plazo_dias:
                    return 'atrasada'
            # Si plazo_dias es None, se considera que no está atrasada
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
        # Actualiza el estado antes de guardar
        self.estado = self.actualizar_estado()

        # Si el objeto ya existe, obtén el estado anterior y 'enviada'
        estado_anterior = None
        enviada_anterior = None
        if self.pk:
            instancia_anterior = self.__class__.objects.get(pk=self.pk)
            estado_anterior = instancia_anterior.estado
            enviada_anterior = instancia_anterior.enviada

        # Guardar los cambios en la base de datos
        super().save(*args, **kwargs)

        # Si 'enviada' cambia de False a True
        if self.enviada and not enviada_anterior:
            tiempo_transcurrido = self.calcular_tiempo_transcurrido()
            self.tiempo_transcurrido_registrado = tiempo_transcurrido['dias'] * 24 * 3600 + tiempo_transcurrido['horas'] * 3600 + tiempo_transcurrido['minutos'] * 60
            # Actualizar solo el campo 'tiempo_transcurrido_registrado' en la base de datos
            super(EtapaBase, self).save(update_fields=['tiempo_transcurrido_registrado'])

        # Si cambia a 'finalizada' desde cualquier otro estado (mantiene la lógica existente)
        if self.estado == 'finalizada' and estado_anterior != 'finalizada':
            self.ultima_finalizacion = timezone.now()
            # Actualizar solo el campo 'ultima_finalizacion' en la base de datos
            super(EtapaBase, self).save(update_fields=['ultima_finalizacion'])
