from django.db import models
from django.conf import settings
#
from applications.etapas.models import Etapa1


class FormularioSectorial(models.Model):

    etapa = models.ForeignKey(Etapa1, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='formularios_sectoriales')
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre