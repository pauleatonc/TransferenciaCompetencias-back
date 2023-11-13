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



"""class Etapa2(EtapaBase):

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
            raise ValidationError("No puede haber más de un usuario activo por sector.")"""