from django.db import models

from applications.base.models import BaseModel
from applications.competencias.models import Competencia
from applications.sectores_gubernamentales.models import SectorGubernamental
from django.utils import timezone


class FormularioSectorial(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, related_name='formulario_sectorial_set')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='formularios_sectoriales')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)
    intento_envio = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.formulario_enviado:
            # Validar y guardar cada paso
            for paso in [self.paso1.first(), self.paso2.first(), self.paso3.first(), self.paso4.first(), self.paso5.first()]:
                if paso is not None:
                    paso.save()

            # Verificar si todos los pasos están completados
            if not self.todos_los_pasos_completados():
                self.intento_envio = True
                self.save(update_fields=['intento_envio'])  # Guardar el cambio en intento_envio
                raise ValueError("No se puede enviar el formulario hasta que todos los pasos estén completados.")

            # Establecer la fecha de envío
            if not self.fecha_envio:
                self.fecha_envio = timezone.now()

        super(FormularioSectorial, self).save(*args, **kwargs)

    def todos_los_pasos_completados(self):
        # Verifica cada paso por su related_name
        pasos_completados = (
            all(paso.completado for paso in self.paso1.all()) and
            all(paso.completado for paso in self.paso2.all()) and
            all(paso.completado for paso in self.paso3.all()) and
            all(paso.completado for paso in self.paso4.all()) and
            all(paso.completado for paso in self.paso5.all())
        )
        return pasos_completados

    def __str__(self):
        return f"{self.nombre} - {self.sector.nombre}"


class PasoBase(BaseModel):
    completado = models.BooleanField(default=False)

    @property
    def campos_obligatorios_completados(self):
        return self.avance()[0] == self.avance()[1]

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