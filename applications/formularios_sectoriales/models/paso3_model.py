from django.db import models
from django.utils.translation import gettext as _

from .base_model import PasoBase, FormularioSectorial
from applications.base.models import BaseModel
from applications.regioncomuna.models import Region


class Paso3Encabezado(PasoBase):

    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='paso3encabezado', null=True, blank=True)
    @property
    def nombre_paso(self):
        return 'Cobertura de la Competencia'

    @property
    def numero_paso(self):
        return 3

    def avance_completo(self):
        pasos3 = Paso3.objects.filter(formulario_sectorial=self.formulario_sectorial)
        total_pasos = pasos3.count()
        pasos_completos = sum(1 for paso in pasos3 if paso.avance().split('/')[0] == paso.avance().split('/')[1])
        return pasos_completos, total_pasos

    def avance(self):
        pasos_completos, total_pasos = self.avance_completo()
        return f"{pasos_completos}/{total_pasos}"


class Paso3(PasoBase):
    def avance_numerico(self):
        # Lista de campos que no son estrictamente numéricos y son obligatorios
        campos_obligatorios_texto = [
            'universo_cobertura', 'descripcion_cobertura'
        ]
        total_campos = len(campos_obligatorios_texto) + 1  # +1 para considerar 'coberturas_anuales_completados'

        # Verifica si los campos de texto obligatorios están llenos
        completados = sum([1 for campo in campos_obligatorios_texto if getattr(self, campo, None)])

        # Verifica si todas las instancias de CoberturaAnual tienen los campos numéricos definidos (no None)
        todas_coberturas_anuales_completas = all(
            cobertura.universo_cobertura is not None and
            cobertura.cobertura_efectivamente_abordada is not None and
            cobertura.recursos_ejecutados is not None
            for cobertura in self.formulario_sectorial.cobertura_anual.all()
        )

        # Si todas las instancias de CoberturaAnual están completas (considerando None como incompleto), añadir 1 a completados
        if todas_coberturas_anuales_completas:
            completados += 1

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"

    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='paso3')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='paso3', null=True, blank=True)

    """Campos descripción Cobertura de la Competencia"""
    universo_cobertura = models.TextField(max_length=800, blank=True)
    descripcion_cobertura = models.TextField(max_length=800, blank=True)


class CoberturaAnual(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='cobertura_anual')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cobertura_anual', null=True, blank=True)
    anio = models.IntegerField()
    universo_cobertura = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    cobertura_efectivamente_abordada = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    recursos_ejecutados = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    class Meta:
        ordering = ['anio']

    @property
    def total_cobertura_efectiva(self):
        # Comprueba si ambos, cobertura_efectivamente_abordada y recursos_ejecutados,
        # tienen valores válidos y diferentes de cero.
        if self.cobertura_efectivamente_abordada and self.recursos_ejecutados and \
                self.cobertura_efectivamente_abordada != 0 and self.recursos_ejecutados != 0:
            return round(self.recursos_ejecutados / self.cobertura_efectivamente_abordada, 2)
        return 'No calculado'

    def __str__(self):
        return f"{self.formulario_sectorial} - {self.anio}"
