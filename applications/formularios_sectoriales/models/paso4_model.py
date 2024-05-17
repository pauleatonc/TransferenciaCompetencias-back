import os
from django.core.validators import FileExtensionValidator
from django.contrib import admin

from .base_model import PasoBase, FormularioSectorial
from django.db import models

from ..functions import organigrama_regional_path
from applications.base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from applications.regioncomuna.models import Region


class Paso4Encabezado(PasoBase):
    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='paso4encabezado', null=True, blank=True)

    @property
    def nombre_paso(self):
        return 'Indicadores de Desempeño'

    @property
    def numero_paso(self):
        return 4

    def avance_numerico(self):
        pasos4 = Paso4.objects.filter(formulario_sectorial=self.formulario_sectorial)
        total_pasos = pasos4.count()
        pasos_completos = sum(1 for paso in pasos4 if paso.avance().split('/')[0] == paso.avance().split('/')[1])
        return pasos_completos, total_pasos

    def avance(self):
        pasos_completos, total_pasos = self.avance_numerico()
        return f"{pasos_completos}/{total_pasos}"


class Paso4(PasoBase):
    def avance_numerico(self):
        # Campos obligatorios en IndicadorDesempeno
        campos_obligatorios_indicador = [
            'indicador', 'formula_calculo', 'descripcion_indicador',
            'medios_calculo', 'verificador_asociado'
        ]

        # Obtiene todas las instancias de IndicadorDesempeno asociadas
        indicadores = self.formulario_sectorial.indicador_desempeno.all()

        # Comprueba que todos los indicadores tienen todos los campos obligatorios completos
        todos_indicadores_completos = all(
            all(getattr(indicador, campo) for campo in campos_obligatorios_indicador)
            for indicador in indicadores
        )

        # Devuelve valores numéricos
        completados = 1 if todos_indicadores_completos else 0
        total_campos = 1

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='paso4')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='paso4', null=True, blank=True)


class IndicadorDesempeno(BaseModel):

    INDICADOR = (
        ('PMG', 'PMG'),
        ('CDC', 'CDC'),
        ('IG', 'Indicador general')
    )

    indicador = models.CharField(max_length=5, choices=INDICADOR, blank=True)
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='indicador_desempeno')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='indicador_desempeno', null=True, blank=True)
    formula_calculo = models.TextField(max_length=500, blank=True)
    descripcion_indicador = models.TextField(max_length=500, blank=True)
    medios_calculo = models.TextField(max_length=1000, blank=True)
    verificador_asociado = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.formulario_sectorial} - {self.indicador} - {self.descripcion_indicador}"

    class Meta:
        ordering = ['created_date']
