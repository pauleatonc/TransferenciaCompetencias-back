import os
from django.core.validators import FileExtensionValidator

from .base_model import PasoBase, FormularioSectorial
from django.db import models

from ..functions import organigrama_regional_path
from ...base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso2(PasoBase):

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

        # Verifica si hay archivos válidos en el set

        return f"{completados}/{total_campos}"

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='encabezado')


class OrganismosIntervinientes(BaseModel):

    ORGANISMO = (
        ('MIN', 'Ministerio o Servicio Público'),
        ('GORE', 'Gobierno Regional'),
        ('DPR', 'Delegación Presidencial Regional'),
        ('OTRO', 'Otro')
    )

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='p_2_1_organismos_intervinientes')
    organismo = models.CharField(max_length=5, choices=ORGANISMO, blank=True)
    sector_ministerio_servicio = models.CharField(max_length=500, blank=True)
    descripcion = models.CharField(max_length=500, blank=True)


class UnidadesIntervinientes(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_2_unidades_intervinientes')
    organismo = models.ForeignKey(OrganismosIntervinientes, on_delete=models.CASCADE, related_name='unidadesintervinientes_set')
    nombre_unidad = models.TextField(max_length=500, blank=True)
    descripcion_unidad = models.TextField(max_length=500, blank=True)


class EtapasEjercicioCompetencia(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_3_etapas_ejercicio_competencia')
    nombre_etapa = models.TextField(max_length=500, blank=True)
    descripcion_etapa = models.TextField(max_length=500, blank=True)


class ProcedimientosEtapas(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='procedimientos')
    etapa = models.ForeignKey(EtapasEjercicioCompetencia, on_delete=models.CASCADE,
                                             related_name='procedimientos')
    descripcion_procedimiento = models.TextField(max_length=500, blank=True)
    unidades_intervinientes = models.ManyToManyField(UnidadesIntervinientes)


class PlataformasySoftwares(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_4_plataformas_y_softwares')
    nombre_plataforma = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    costo_adquisicion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_mantencion_anual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descripcion_costos = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    funcion_plataforma = models.TextField(max_length=500, blank=True)
    etapas = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='PlataformasySoftwares_set', blank=True)
    capacitacion_plataforma = models.BooleanField(blank=True, default=False)


class FlujogramaCompetencia(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_5_flujograma_competencia')
    flujograma_competencia = models.FileField(upload_to='formulario_sectorial',
                                            validators=[
                                                FileExtensionValidator(
                                                    ['pdf'], message='Solo se permiten archivos PDF.'),
                                                validate_file_size_twenty],
                                            verbose_name='Flujograma de ejercicio de la Competencia', blank=True, null=True)
    descripcion_cualitativa = models.TextField(max_length=500, blank=True)
