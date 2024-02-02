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

    def avance(self):
        completados = 0
        total_campos = 3

        # Verificar UnidadesIntervinientes
        unidades_intervinientes_completas = all(
            unidad.nombre_unidad and unidad.descripcion_unidad
            for unidad in self.formulario_sectorial.p_2_2_unidades_intervinientes.all()
        )
        if unidades_intervinientes_completas:
            completados += 1

        # Verificar PlataformasySoftwares
        plataformas_completas = any(
            plataforma.nombre_plataforma and plataforma.descripcion_tecnica and
            plataforma.costo_adquisicion is not None and plataforma.costo_mantencion_anual is not None and
            plataforma.descripcion_costos and plataforma.descripcion_tecnica and
            plataforma.funcion_plataforma for plataforma in
            self.formulario_sectorial.p_2_4_plataformas_y_softwares.all()
        )
        if plataformas_completas:
            completados += 1

        # Verificar FlujogramaCompetencia
        flujograma_completo = any(
            flujograma.flujograma_competencia and flujograma.descripcion_cualitativa
            for flujograma in self.formulario_sectorial.p_2_5_flujograma_competencia.all()
        )
        if flujograma_completo:
            completados += 1

        return f"{completados}/{total_campos}"

    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='paso2')

    def save(self, *args, **kwargs):
        if self.campos_obligatorios_completados:
            self.completado = True
        else:
            self.completado = False
        super(Paso2, self).save(*args, **kwargs)


class OrganismosIntervinientes(BaseModel):

    ORGANISMO = (
        ('MIN', 'Ministerio o Servicio Público'),
        ('GORE', 'Gobierno Regional'),
        ('DPR', 'Delegación Presidencial Regional'),
        ('OTRO', 'Otro')
    )

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='p_2_1_organismos_intervinientes')
    organismo = models.CharField(max_length=5, choices=ORGANISMO, blank=True)
    nombre_ministerio_servicio = models.CharField(max_length=500, blank=True)
    descripcion = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['id']


class UnidadesIntervinientes(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_2_unidades_intervinientes')
    organismo = models.ForeignKey(OrganismosIntervinientes, on_delete=models.CASCADE, related_name='unidadesintervinientes')
    nombre_unidad = models.TextField(max_length=500, blank=True)
    descripcion_unidad = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['id']


class EtapasEjercicioCompetencia(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_3_etapas_ejercicio_competencia')
    nombre_etapa = models.TextField(max_length=500, blank=True)
    descripcion_etapa = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['id']


class ProcedimientosEtapas(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='procedimientos')
    etapa = models.ForeignKey(EtapasEjercicioCompetencia, on_delete=models.CASCADE,
                                             related_name='procedimientos')
    descripcion_procedimiento = models.TextField(max_length=500, blank=True)
    unidades_intervinientes = models.ManyToManyField(UnidadesIntervinientes, blank=True)

    class Meta:
        ordering = ['id']


class PlataformasySoftwares(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_2_4_plataformas_y_softwares')
    nombre_plataforma = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    costo_adquisicion = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    costo_mantencion_anual = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    descripcion_costos = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    funcion_plataforma = models.TextField(max_length=500, blank=True)
    etapas = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='PlataformasySoftwares_set', blank=True)
    capacitacion_plataforma = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['id']


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
