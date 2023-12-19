import os
from django.core.validators import FileExtensionValidator
from django.contrib import admin

from .base_model import PasoBase, FormularioSectorial
from django.db import models

from ..functions import organigrama_regional_path
from ...base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso4(PasoBase):

    @property
    def nombre_paso(self):
        return 'Indicadores de Desempeño'

    @property
    def numero_paso(self):
        return 4

    @property
    def campos_obligatorios_completados(self):
        return self.avance()[0] == self.avance()[1]

    def avance(self):
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

        # Devuelve '1/1' si todos los indicadores están completos, de lo contrario '0/1'
        return "1/1" if todos_indicadores_completos else "0/1"

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='paso4')


class IndicadorDesempeno(BaseModel):

    INDICADOR = (
        ('PMG', 'PMG'),
        ('CDC', 'CDC'),
        ('IG', 'Indicador general')
    )

    indicador = models.CharField(max_length=5, choices=INDICADOR, blank=True)
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='indicador_desempeno')
    formula_calculo = models.TextField(max_length=500, blank=True)
    descripcion_indicador = models.TextField(max_length=500, blank=True)
    medios_calculo = models.TextField(max_length=500, blank=True)
    verificador_asociado = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.formulario_sectorial} - {self.indicador} - {self.descripcion_indicador}"
