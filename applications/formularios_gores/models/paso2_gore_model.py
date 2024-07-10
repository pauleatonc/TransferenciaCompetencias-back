from django.db import models

from applications.base.models import BaseModel
from applications.formularios_sectoriales.models import (
    Subtitulos,
    ItemSubtitulo,
)
from applications.sectores_gubernamentales.models import SectorGubernamental
from .base_model import PasoBase, FormularioGORE


class Paso2(PasoBase):

    @property
    def nombre_paso(self):
        return 'Estimación de recursos económicos'

    @property
    def numero_paso(self):
        return 2

    def es_instancia_costos_completa(self, instancia):
        # Verificar según id_sectorial y subtitulo
        if instancia.id_sectorial is not None:
            if instancia.subtitulo and instancia.subtitulo.subtitulo == 'Sub. 21':
                return True
            campos_requeridos = ['total_anual_gore', 'descripcion', 'es_transitorio']
        else:
            campos_requeridos = ['total_anual_gore', 'descripcion', 'es_transitorio', 'item_subtitulo']

        # Verifica que todos los campos requeridos estén completos
        return all(getattr(instancia, campo, None) is not None for campo in campos_requeridos)

    def es_fluctuacion_completa(self, fluctuacion):
        # Verificar que el campo 'descripcion' de FluctuacionPresupuestaria está completo
        if fluctuacion.descripcion is None or fluctuacion.descripcion.strip() == '':
            return False

        # Verificar que todos los costos de CostoAnioGore asociados tienen 'costo' lleno
        costos_anio = CostoAnioGore.objects.filter(evolucion_gasto=fluctuacion)
        return all(costo.costo is not None for costo in costos_anio)

    def avance_numerico(self):
        costos_directos = CostosDirectosGore.objects.filter(formulario_gore_id=self.formulario_gore_id)
        completados_costos_directos = all(self.es_instancia_costos_completa(costo) for costo in costos_directos)

        costos_indirectos = CostosIndirectosGore.objects.filter(formulario_gore_id=self.formulario_gore_id)
        completados_costos_indirectos = all(self.es_instancia_costos_completa(costo) for costo in costos_indirectos)

        fluctuacion_gasto = FluctuacionPresupuestaria.objects.filter(formulario_gore=self.formulario_gore)
        completados_fluctuacion_gasto = all(self.es_fluctuacion_completa(fluctuacion) for fluctuacion in fluctuacion_gasto)

        total_campos = 3
        completados = (1 if completados_costos_directos else 0) + (1 if completados_costos_indirectos else 0) + (1 if completados_fluctuacion_gasto else 0)

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"

    formulario_gore = models.OneToOneField(FormularioGORE, on_delete=models.CASCADE, related_name='paso2_gore')
    

class CostosDirectosGore(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_2_1_a_costos_directos')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='costos_directos_gore', blank=True, null=True)
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='costos_directos_gore', blank=True, null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_directos_gore', blank=True, null=True)
    total_anual_sector = models.IntegerField(null=True, blank=True)
    total_anual_gore = models.IntegerField(null=True, blank=True)
    es_transitorio = models.BooleanField(blank=True, null=True, default=None)
    diferencia_monto = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)
    id_sectorial = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.total_anual_sector is not None and self.total_anual_gore is not None:
            self.diferencia_monto = self.total_anual_sector - self.total_anual_gore
        else:
            self.diferencia_monto = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_date']


class CostosIndirectosGore(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                        related_name='p_2_1_b_costos_indirectos')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='costos_indirectos_gore',
                               blank=True, null=True)
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='costos_indirectos_gore', blank=True,
                                  null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_indirectos_gore', blank=True, null=True)
    total_anual_sector = models.IntegerField(null=True, blank=True)
    total_anual_gore = models.IntegerField(null=True, blank=True)
    es_transitorio = models.BooleanField(blank=True, null=True, default=None)
    diferencia_monto = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)
    id_sectorial = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.total_anual_sector is not None and self.total_anual_gore is not None:
            self.diferencia_monto = self.total_anual_sector - self.total_anual_gore
        else:
            self.diferencia_monto = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_date']


class ResumenCostosGore(BaseModel):
    """Modelo para almacenar el resumen de costos"""
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='resumen_costos')
    # Resumen costos directos
    directos_por_sector = models.IntegerField(null=True, blank=True)
    directos_por_gore = models.IntegerField(null=True, blank=True)
    diferencia_directos = models.IntegerField(null=True, blank=True)

    # Resumen costos indirectos
    indirectos_por_sector = models.IntegerField(null=True, blank=True)
    indirectos_por_gore = models.IntegerField(null=True, blank=True)
    diferencia_indirectos = models.IntegerField(null=True, blank=True)

    # Resumen total
    costos_sector = models.IntegerField(null=True, blank=True)
    costos_gore = models.IntegerField(null=True, blank=True)
    diferencia_costos = models.IntegerField(null=True, blank=True)


class FluctuacionPresupuestaria(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_2_1_c_fluctuaciones_presupuestarias')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='fluctuacion_presupuestaria', blank=True, null=True)
    descripcion = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['subtitulo']


class CostoAnioGore(BaseModel):
    evolucion_gasto = models.ForeignKey(FluctuacionPresupuestaria, on_delete=models.CASCADE, related_name='costo_anio_gore')
    anio = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    class Meta:
        ordering = ['anio']
