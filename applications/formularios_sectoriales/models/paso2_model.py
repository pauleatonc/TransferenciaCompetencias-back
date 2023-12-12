import os
from django.core.validators import FileExtensionValidator

from .base_model import PasoBase
from django.db import models

from ..functions import organigrama_regional_path
from ...base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso1(PasoBase):

    @property
    def nombre_paso(self):
        return 'Arquitectura de Procesos'

    @property
    def numero_paso(self):
        return 2

    @property
    def campos_obligatorios_completados(self):
        return self.avance()[0] == self.avance()[1]

    def avance(self):
        # Lista de todos los campos obligatorios
        campos_obligatorios = [
            'forma_juridica_organismo', 'mision_institucional',
            'identificacion_competencia', 'organigrama_nacional', 'fuentes_normativas',
            'territorio_competencia', 'enfoque_territorial_competencia',
            'ambito', 'posibilidad_ejercicio_por_gobierno_regional',
            'organo_actual_competencia'
        ]
        total_campos = len(campos_obligatorios)

        # Verifica si los campos obligatorios están llenos
        completados = sum([1 for campo in campos_obligatorios if getattr(self, campo, None)])

        # Verifica si hay archivos válidos en el set de MarcoJuridico
        marco_juridico_completados = sum(
            [1 for marco in self.marcojuridico_set.all() if marco.documento and marco.documento.name])
        total_campos += self.marcojuridico_set.count()

        completados += marco_juridico_completados

        return f"{completados}/{total_campos}"


class OrganismosIntervinientes(BaseModel):
    organismo = models.TextField(max_length=500, blank=True)


class UnidadesIntervinientes(BaseModel):
    organismo = models.ForeignKey(OrganismosIntervinientes, on_delete=models.CASCADE, related_name='unidadesintervinientes_set')
    descripcion_unidad = models.TextField(max_length=500, blank=True)


class EtapasEjercicioCompetencia(BaseModel):
    nombre_etapa = models.TextField(max_length=500, blank=True)
    descripcion_etapa = models.TextField(max_length=500, blank=True)


class ProcedimientosEtapas(BaseModel):
    descripcion_procedimiento = models.TextField(max_length=500, blank=True)
    unidades_intervinientes = models.ManyToManyField(UnidadesIntervinientes, on_delete=models.CASCADE, related_name='ProcedimientosEtapas_set')


class PlataformasySoftwares(BaseModel):
    nombre_plataforma = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    costo_adquisicion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_mantencion_anual = models.DecimalField(blank=True)
    descripcion_costos = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    funcion_plataforma = models.TextField(max_length=500, blank=True)
    etapas = models.ManyToManyField(EtapasEjercicioCompetencia, on_delete=models.CASCADE,
                                                     related_name='PlataformasySoftwares_set')
    capacitacion_plataforma = models.BooleanField(blank=True)
