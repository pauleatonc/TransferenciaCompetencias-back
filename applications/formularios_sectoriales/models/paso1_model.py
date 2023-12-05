from django.core.validators import FileExtensionValidator

from .base_model import PasoBase
from django.db import models

from ...base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso1(PasoBase):

    AMBITO = (
        ('AP', 'Fomento de las Actividades Productivas'),
        ('OT', 'Ordenamiento Territorial'),
        ('DSC', 'Desarrollo Social y Cultural')
    )

    @property
    def nombre_paso(self):
        return 'Descripción de la Institución'

    def contar_campos_obligatorios_completados(self):
        campos_obligatorios = ['forma_juridica_organismo',
                               'mision_institucional',
                               'identificacion_competencia',
                               'fuentes_normativas',
                               'territorio_competencia',
                               'enfoque_territorial_competencia',
                               'ambito',
                               'posibilidad_ejercicio_por_gobierno_regional',
                               'organo_actual_competencia'
                               ]
        completados = sum([1 for campo in campos_obligatorios if getattr(self, campo)])

        tiene_archivos_campojuridico = self.marcojuridico_set.exists()
        if tiene_archivos_campojuridico:
            completados += 1

        return completados

    """1.1  Ficha de descripción organizacional"""
    forma_juridica_organismo = models.TextField(max_length=500, blank=True)
    descripcion_archivo_marco_juridico = models.TextField(max_length=500, blank=True)
    mision_institucional = models.TextField(max_length=500, blank=True)
    informacion_adicional_marco_juridico = models.TextField(max_length=500, blank=True)


    """1.2 Organización Institucional"""
    organigrama_nacional = models.FileField(upload_to='formulario_sectorial',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Organigrama Nacional', blank=True, null=True)
    descripcion_archivo_organigrama_regional = models.TextField(max_length=500, blank=True)


    """1.3 Marco Regulatorio y funcional de la competencia"""
    identificacion_competencia = models.TextField(max_length=500, blank=True)
    fuentes_normativas = models.TextField(max_length=500, blank=True)
    territorio_competencia = models.TextField(max_length=500, blank=True)
    enfoque_territorial_competencia = models.TextField(max_length=500, blank=True)
    ambito = models.CharField(max_length=5, choices=AMBITO, blank=True)
    posibilidad_ejercicio_por_gobierno_regional = models.TextField(max_length=500, blank=True)
    organo_actual_competencia = models.TextField(max_length=500, blank=True)

    def clean(self):
        super().clean()
        num_archivos = self.marcojuridico_set.count()
        if num_archivos < 1 or num_archivos > 5:
            from django.core.exceptions import ValidationError
            raise ValidationError("Debes subir entre 1 y 5 archivos para el marco jurídico.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class MarcoJuridico(BaseModel):
    paso1 = models.ForeignKey(Paso1, on_delete=models.CASCADE, related_name='marcojuridico_set')
    documento = models.FileField(upload_to='formulario_sectorial',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Marco jurídico que lo rige', blank=True, null=True)


class OrganigramaRegional(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='organigramas_regionales')
    paso1 = models.ForeignKey(Paso1, on_delete=models.CASCADE, related_name='organigramaregional_set')
    documento = models.FileField(upload_to='formulario_sectorial',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Organigrama Regional', blank=True, null=True)