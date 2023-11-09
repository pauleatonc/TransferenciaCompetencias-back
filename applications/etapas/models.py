from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import Q
#
from applications.competencias.models import Competencia
from applications.base.functions import TWENTY_SIZE_LIMIT

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
    usuarios = models.ManyToManyField(User, related_name="%(class)s_usuarios")
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
        return self.usuarios.exists()

    def save(self, *args, **kwargs):
        if self.usuario_sectorial_vinculado and not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()  # Asignar la fecha de inicio al momento de asignar usuarios
            self.plazo_dias = self.competencia.plazo_formulario_sectorial
            self.aprobada = True
        super().save(*args, **kwargs)

# Este receptor se activará cada vez que los usuarios de una etapa sean modificados.
@receiver(m2m_changed, sender=EtapaBase.usuarios.through)
def usuarios_cambiados(sender, instance, **kwargs):
    if instance.usuario_sectorial_vinculado:
        instance.save()


class Etapa2(EtapaBase):

    comentario_observacion = models.TextField(max_length=500, blank=True)
    archivo_observacion = models.FileField(upload_to='observaciones',
                             validators=[
                                 FileExtensionValidator(
                                     ['pdf'], message='Solo se permiten archivos PDF.'), TWENTY_SIZE_LIMIT],
                             verbose_name='Archivo Observación')
    observacion_enviada = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Etapas 2"

    @property
    def usuarios_sectoriales(self):
        # Realiza un filtro buscando usuarios sectoriales
        return self.usuarios.filter(groups__name='Usuario Sectorial')

    @property
    def estado_usuarios_sectoriales(self):
        # Si encuentra alguno da por finalizada la subetapa
        return 'Finalizada' if self.usuarios_sectoriales.exists() else 'Pendiente'

    def save(self, *args, **kwargs):
        # Validación de observación enviada
        if self.observacion_enviada and not self.archivo_observacion:
            raise ValidationError("No se puede enviar la observación sin un archivo de observación.")

        # Actualización de estados de EtapaBase
        if self.observacion_enviada:
            self.enviada = False
            self.aprobada = True

        super().save(*args, **kwargs)

    @property
    def estado_observacion(self):
        return 'Finalizada' if self.observacion_enviada else 'Subir Observaciones'

    def clean(self):
        # Validación personalizada
        super().clean()  # Llamamos al método clean base
        if self.observacion_enviada and not self.archivo_observacion:
            raise ValidationError("No se puede marcar 'observacion_enviada' sin cargar un archivo de observación.")


# Receptor de señal para la validación de un único usuario activo por sector
@receiver(m2m_changed, sender=EtapaBase.usuarios.through)
def validar_usuarios_por_sector(sender, instance, **kwargs):
    if kwargs['action'] in ['post_add', 'post_remove', 'post_clear']:
        usuarios_activos = instance.usuarios.filter(is_active=True)
        sectores = [usuario.sector for usuario in usuarios_activos]
        if len(sectores) != len(set(sectores)):
            raise ValidationError("No puede haber más de un usuario activo por sector.")