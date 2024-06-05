import os
from django.core.validators import FileExtensionValidator

from .base_model import PasoBase, FormularioSectorial
from django.db import models

from applications.formularios_sectoriales.functions import organigrama_regional_path
from applications.base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from applications.regioncomuna.models import Region
from applications.competencias.models import Ambito
from django.core.exceptions import ValidationError


class Paso1(PasoBase):

    @property
    def nombre_paso(self):
        return 'Descripción de la Institución'

    @property
    def numero_paso(self):
        return 1

    def avance_numerico(self):
        # Lista de todos los campos obligatorios
        campos_obligatorios = [
            'forma_juridica_organismo', 'mision_institucional',
            'identificacion_competencia', 'organigrama_nacional', 'fuentes_normativas',
            'territorio_competencia', 'enfoque_territorial_competencia',
            'ambito_paso1', 'posibilidad_ejercicio_por_gobierno_regional',
            'organo_actual_competencia'
        ]
        total_campos = len(campos_obligatorios) + 1  # Incrementar en uno por el archivo en MarcoJuridico

        # Verifica si los campos obligatorios están llenos
        completados = sum([1 for campo in campos_obligatorios if getattr(self, campo, None)])

        # Verificar si hay al menos un archivo en MarcoJuridico
        marco_juridico_count = self.formulario_sectorial.marcojuridico.count()
        if marco_juridico_count > 0:
            completados += 1

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"

    @property
    def multiplicador_caracteres_region(self):
        # Accede a las regiones asociadas a la competencia a través del formulario sectorial
        competencia = self.formulario_sectorial.competencia
        numero_regiones = competencia.regiones.count()

        if numero_regiones == 1:
            return 500
        else:
            return 300 + numero_regiones * 200

    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='paso1')

    """1.1  Ficha de descripción organizacional"""
    forma_juridica_organismo = models.TextField(max_length=9000, blank=True)
    descripcion_archivo_marco_juridico = models.TextField(max_length=9000, blank=True)
    mision_institucional = models.TextField(max_length=9000, blank=True)
    informacion_adicional_marco_juridico = models.TextField(max_length=9000, blank=True)


    """1.2 Organización Institucional"""
    organigrama_nacional = models.FileField(upload_to='formulario_sectorial',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Organigrama Nacional', blank=True, null=True)
    descripcion_archivo_organigrama_nacional = models.TextField(max_length=9000, blank=True)
    descripcion_archivo_organigrama_regional = models.TextField(max_length=9000, blank=True)


    """1.3 Marco Regulatorio y funcional de la competencia"""
    identificacion_competencia = models.TextField(max_length=9000, blank=True)
    fuentes_normativas = models.TextField(max_length=9000, blank=True)
    territorio_competencia = models.TextField(max_length=9000, blank=True)
    enfoque_territorial_competencia = models.TextField(max_length=9000, blank=True)
    ambito_paso1 = models.ForeignKey(Ambito, on_delete=models.CASCADE, related_name='paso1', null=True, blank=True)
    posibilidad_ejercicio_por_gobierno_regional = models.TextField(max_length=9000, blank=True)
    organo_actual_competencia = models.TextField(max_length=9000, blank=True)


class MarcoJuridico(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='marcojuridico')
    documento = models.FileField(upload_to='formulario_sectorial',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Marco jurídico que lo rige', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Contar cuántos documentos ya existen para este Formulario Sectorial
        existing_files_count = MarcoJuridico.objects.filter(
            formulario_sectorial=self.formulario_sectorial).count()

        if existing_files_count >= 5:
            # No permitir guardar si ya hay 5 o más archivos
            raise ValidationError('No se pueden añadir más de 5 marcos jurídicos para este formulario.')

        super().save(*args, **kwargs)


class OrganigramaRegional(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='organigramas_regionales')
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='organigramaregional')
    documento = models.FileField(
        upload_to = organigrama_regional_path,
        validators = [
            FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'),
            validate_file_size_twenty
        ],
        verbose_name='Organigrama Regional',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['region']