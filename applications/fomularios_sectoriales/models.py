from django.db import models
#
from applications.etapas.models import Etapa2


class FormularioSectorial(models.Model):

    etapa = models.ForeignKey(Etapa2, on_delete=models.CASCADE
    nombre = models.CharField(max_length=200, unique=True)
    formulario_enviado = models.BooleanField(default=False)