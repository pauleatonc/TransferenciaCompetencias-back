import os
from django.core.validators import FileExtensionValidator

from . import EtapasEjercicioCompetencia
from .base_model import PasoBase, FormularioSectorial
from django.db import models

from ..functions import organigrama_regional_path
from ...base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso5(PasoBase):

    @property
    def nombre_paso(self):
        return 'Costeo de la Competencia'

    @property
    def numero_paso(self):
        return 5

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

        # Verifica si hay archivos válidos en el set

        return f"{completados}/{total_campos}"

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='paso5')

    """5.1 Costos asociados al ejercicio de la competencia"""
    total_costos_directos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_costos_indirectos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costos_totales = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    """5.2 Costos asociados al ejercicio de la competencia"""
    glosas_especificas = models.TextField(max_length=500, blank=True)


class Subtitulos(models.Model):
    subtitulo = models.CharField(max_length=10, unique=True)


class ItemSubtitulo(models.Model):
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='items')
    item = models.CharField(max_length=100, unique=True)


class CostosDirectos(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_a_costos_directos')
    etapa = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='costos_directos', blank=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_directos')
    total_anual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    es_transversal = models.BooleanField(default=False, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)


class CostosIndirectos(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_b_costos_indirectos')
    etapa = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='costos_indirectos')
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_indirectos')
    total_anual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    es_transversal = models.BooleanField(default=False, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)


class ResumenCostosPorSubtitulo(BaseModel):
    """Modelo para almacenar el resumen de costos por subtitulo."""
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_c_resumen_costos_por_subtitulo')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='resumen_costos')
    total_anual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descripcion = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.subtitulo.subtitulo} - Total Anual: {self.total_anual}"

    @classmethod
    def actualizar_resumen(cls, subtitulo_id, formulario_sectorial_id):
        obj, created = cls.objects.update_or_create(
            subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        )


class CostoAnio(BaseModel):
    anio = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class EvolucionGastoAsociado(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='p_5_2_evolucion_gasto_asociado')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='evolucion_gasto_asociado')
    costo_anio = models.ManyToManyField(CostoAnio, related_name='evolucion_gasto_asociado')
    descripcion = models.TextField(max_length=500, blank=True)


class VariacionPromedio(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='p_5_2_variacion_promedio')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='variacion_promedio')
    gasto_n_5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gasto_n_1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    variacion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)

