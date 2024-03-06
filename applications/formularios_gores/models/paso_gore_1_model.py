import os
from django.core.validators import FileExtensionValidator

from .base_model import PasoBase, FormularioGORE
from django.db import models

from applications.base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from django.core.exceptions import ValidationError


class Paso1(PasoBase):

    @property
    def nombre_paso(self):
        return 'Proyección del ejercicio de la competencia'

    @property
    def numero_paso(self):
        return 1

    def avance_numerico(self):
        # Lista de todos los campos obligatorios
        campos_obligatorios = [
            'descripcion_ejercicio_competencia', 'organigrama_gore'
        ]
        total_campos = len(campos_obligatorios) + 1  # Incrementar en uno por el archivo en MarcoJuridico

        # Verifica si los campos obligatorios están llenos
        completados = sum([1 for campo in campos_obligatorios if getattr(self, campo, None)])

        # Verificar si hay al menos un archivo en MarcoJuridico
        flujograma_count = self.formulario_gore.flujograma_ejercicio_competencia.count()
        if flujograma_count > 0:
            completados += 1

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"

    formulario_gore = models.OneToOneField(FormularioGORE, on_delete=models.CASCADE, related_name='paso1')

    """1.1 Descripción del ejercicio de la competencia en el Gobierno Regional"""
    descripcion_ejercicio_competencia = models.TextField(max_length=8800, blank=True)


    """1.3 Organigrama del Gobierno Regional que identifique dónde se alojará la competencia"""
    organigrama_gore = models.FileField(upload_to='formulario_gore',
                                                        validators=[
                                                            FileExtensionValidator(
                                                                ['pdf'], message='Solo se permiten archivos PDF.'),
                                                            validate_file_size_twenty],
                                                        verbose_name='Organigrama GORE competencia',
                                                        blank=True, null=True)
    descripcion_organigrama_gore = models.TextField(max_length=500, blank=True)


class FlujogramaEjercicioCompetencia(BaseModel):
    """1.2 Flujograma de ejercicio de la competencia"""
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE, related_name='flujograma_ejercicio_competencia')
    documento = models.FileField(upload_to='formulario_gore',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_twenty],
                                 verbose_name='Flujograma ejercicio de la competencia', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Contar cuántos Flujogramas ya existen para este FormularioGORE
        existing_files_count = FlujogramaEjercicioCompetencia.objects.filter(
            formulario_gore=self.formulario_gore).count()

        if existing_files_count >= 3:
            # No permitir guardar si ya hay 3 o más archivos
            raise ValidationError('No se pueden añadir más de 3 flujogramas por formulario.')

        super().save(*args, **kwargs)