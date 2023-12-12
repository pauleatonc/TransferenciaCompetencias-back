import os
from django.core.validators import FileExtensionValidator
from django.contrib import admin

from .base_model import PasoBase, FormularioSectorial
from django.db import models

from ..functions import organigrama_regional_path
from ...base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso3(PasoBase):

    @property
    def nombre_paso(self):
        return 'Cobertura de la Competencia'

    @property
    def numero_paso(self):
        return 3

    @property
    def campos_obligatorios_completados(self):
        return self.avance()[0] == self.avance()[1]

    def avance(self):
        # Lista de todos los campos obligatorios
        campos_obligatorios = [
            'universo_cobertura', 'descripcion_cobertura'
        ]
        total_campos = len(campos_obligatorios)

        # Verifica si los campos obligatorios están llenos
        completados = sum([1 for campo in campos_obligatorios if getattr(self, campo, None)])

        # Verifica si hay instancias de CoberturaAnual con todos los campos llenos
        coberturas_anuales_completados = sum(
            [1 for cobertura in self.formulario_sectorial.coberturaanual_set.all()
             if cobertura.universo_cobertura and cobertura.cobertura_efectivamente_abordada and cobertura.recursos_ejecutados])

        # Actualizar el total de campos considerando las instancias de CoberturaAnual
        total_campos += self.formulario_sectorial.coberturaanual_set.count() * 3  # Multiplicar por la cantidad de campos a verificar en CoberturaAnual

        completados += coberturas_anuales_completados

        return f"{completados}/{total_campos}"

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='paso3')

    """Campos descripción Cobertura de la Competencia"""
    universo_cobertura = models.TextField(max_length=800, blank=True)
    descripcion_cobertura = models.TextField(max_length=800, blank=True)


class CoberturaAnual(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='coberturaanual_set')
    anio = models.IntegerField()
    universo_cobertura = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cobertura_efectivamente_abordada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recursos_ejecutados = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def total_cobertura_efectiva(self):
        if self.cobertura_efectivamente_abordada and self.cobertura_efectivamente_abordada != 0:
            return self.recursos_ejecutados / self.cobertura_efectivamente_abordada
        return _('No calculado')

    def __str__(self):
        return f"{self.formulario_sectorial} - {self.anio}"
