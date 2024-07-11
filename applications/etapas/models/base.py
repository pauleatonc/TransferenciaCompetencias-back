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
    fecha_enviada = models.DateTimeField(null=True, blank=True)
    fecha_aprobada = models.DateTimeField(null=True, blank=True)
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
        # Primero verificar si la etapa está aprobada
        if self.aprobada:
            return 'finalizada'
        # Verificar si la etapa está omitida
        elif self.omitida:
            return 'omitida'
        # Si no tiene fecha de inicio, está no iniciada
        elif not self.fecha_inicio:
            return 'no_iniciada'
        # Si está enviada pero aún no aprobada
        elif self.enviada:
            return 'en_revision'
        # Verificar condiciones de plazo y tiempo transcurrido
        else:
            if self.plazo_dias is not None:
                tiempo_transcurrido = self.calcular_tiempo_transcurrido()
                if tiempo_transcurrido['dias'] > self.plazo_dias:
                    return 'atrasada'
            # Por defecto, si no cumple las condiciones anteriores
            return 'en_estudio'

    def segundos_restantes(self):
        if self.fecha_inicio and self.plazo_dias is not None:
            tiempo_actual = timezone.now()
            delta = tiempo_actual - self.fecha_inicio
            return max(self.plazo_dias * 24 * 3600 - delta.total_seconds(), 0)
        return 0

    def calcular_tiempo_transcurrido(self):
        """
        Calcula el tiempo transcurrido en segundos desde fecha_inicio hasta la fecha actual o hasta fecha_enviada si enviada es True.
        """
        if not self.fecha_inicio:
            return {'dias': 0, 'horas': 0, 'minutos': 0}

        # Determina el punto final del cálculo en base a si enviada es True y fecha_enviada está definida
        tiempo_final = self.fecha_enviada if self.enviada and self.fecha_enviada else timezone.now()

        delta = tiempo_final - self.fecha_inicio
        total_seconds = int(delta.total_seconds())
        dias = total_seconds // (24 * 3600)
        horas = (total_seconds % (24 * 3600)) // 3600
        minutos = (total_seconds % 3600) // 60

        return {'dias': dias, 'horas': horas, 'minutos': minutos}

    def save(self, *args, **kwargs):
        # Actualiza el estado antes de cualquier operación de guardado
        self.estado = self.actualizar_estado()

        # Si '_saving' está activo, simplemente guarda sin modificar nada más para evitar recursión
        if hasattr(self, '_saving'):
            super().save(*args, **kwargs)
            return

        # Previene la recursión con una bandera temporal
        self._saving = True

        # Comprobar y registrar cambios en 'enviada' y 'aprobada' antes de guardar los cambios
        if self.pk:
            instancia_anterior = self.__class__.objects.get(pk=self.pk)
            if not instancia_anterior.enviada and self.enviada:
                self.fecha_enviada = timezone.now()
            if not instancia_anterior.aprobada and self.aprobada:
                self.fecha_aprobada = timezone.now()

        # Realiza el guardado principal
        super().save(*args, **kwargs)
        self._saving = False

    def tiempo_llenado_formulario(self):
        if self.fecha_inicio and self.fecha_enviada:
            return (self.fecha_enviada - self.fecha_inicio).total_seconds()
        return 0

    def tiempo_revision_subdere(self):
        if self.fecha_enviada and self.fecha_aprobada:
            return (self.fecha_aprobada - self.fecha_enviada).total_seconds()
        return 0

    def tiempo_total_etapa(self):
        if self.fecha_inicio and self.fecha_aprobada:
            return (self.fecha_aprobada - self.fecha_inicio).total_seconds()
        return 0
