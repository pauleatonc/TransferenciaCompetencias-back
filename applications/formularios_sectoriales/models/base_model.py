from django.core.validators import FileExtensionValidator
from django.db import models

from applications.base.functions import validate_file_size_twenty
from applications.base.models import BaseModel
from applications.competencias.models import Competencia
from applications.sectores_gubernamentales.models import SectorGubernamental
from django.utils import timezone


class FormularioSectorial(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, related_name='formulario_sectorial')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='formularios_sectoriales')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)
    intento_envio = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    antecedente_adicional_sectorial = models.FileField(upload_to='formulario_sectorial',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Antecedentes adicionales formulario sectorial', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.formulario_enviado and not self.todos_los_pasos_completados():
            self.intento_envio = True
            super(FormularioSectorial, self).save(update_fields=['intento_envio'])
            raise ValueError("No se puede enviar el formulario hasta que todos los pasos estén completados.")

        # Si el formulario está siendo enviado y todos los pasos están completados,
        # entonces proceder normalmente con la lógica de guardado.
        if self.formulario_enviado:
            # Validar y guardar cada paso
            pasos = [self.paso1, self.paso2, self.paso3, self.paso4, self.paso5]
            for paso in pasos:
                if paso is not None:
                    paso.save()

            # Establecer la fecha de envío si aún no se ha establecido
            if not self.fecha_envio:
                self.fecha_envio = timezone.now()
                kwargs['update_fields'] = ['fecha_envio'] if 'update_fields' in kwargs and kwargs[
                    'update_fields'] is not None else None

        # Finalmente, llamar al método save de la clase base para completar el guardado del modelo.
        super(FormularioSectorial, self).save(*args, **kwargs)

    def todos_los_pasos_completados(self):
        pasos = [self.paso1, self.paso2, self.paso3, self.paso4, self.paso5]

        pasos_completados = all(paso is not None and paso.completado for paso in pasos)

        return pasos_completados

    def __str__(self):
        return f"{self.nombre} - {self.sector.nombre}"


class PasoBase(BaseModel):

    @property
    def completado(self):
        return self.campos_obligatorios_completados

    @property
    def campos_obligatorios_completados(self):
        completados, total_campos = self.avance_numerico()
        return completados == total_campos

    @property
    def estado_stepper(self):
        if self.campos_obligatorios_completados:
            return 'done'
        elif self.formulario_sectorial.intento_envio and not self.campos_obligatorios_completados:
            return 'warning'
        else:
            return 'default'

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} - {self.formulario_sectorial.nombre}"