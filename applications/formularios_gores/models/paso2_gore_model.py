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
        # Mantén la lista de campos requeridos, excepto 'es_transversal'
        campos_requeridos = [
            'total_anual_gore', 'descripcion'
        ]

        # Verifica primero que los campos distintos a 'es_transversal' no sean None
        campos_completos = all(getattr(instancia, campo, None) is not None for campo in campos_requeridos)

        # Luego verifica específicamente 'es_transitorio' para asegurar que no sea None
        es_transitorio_completo = getattr(instancia, 'es_transitorio', None) is not None

        # Un ítem está completo si todos los campos están completos y 'es_transitorio' no es None
        completa = campos_completos and es_transitorio_completo

        return completa

    def es_fluctuacion_completa(self, instancia):
        return all([
            instancia.subtitulo_id,
            CostoAnioGore.objects.filter(evolucion_gasto=instancia).exists()
        ]) and all(
            getattr(anio, 'costo', None) is not None
            for anio in CostoAnioGore.objects.filter(evolucion_gasto=instancia)
        )

    def avance_numerico(self):
        # Verifica instancias de CostosDirectos y CostosIndirectos
        costos_directos = CostosDirectosGore.objects.filter(formulario_gore_id=self.formulario_gore_id)
        total_costos_directos = costos_directos.count()
        completados_costos_directos = sum([1 for costo in costos_directos if self.es_instancia_costos_completa(costo)])

        costos_indirectos = CostosIndirectosGore.objects.filter(formulario_gore_id=self.formulario_gore_id)
        total_costos_indirectos = costos_indirectos.count()
        completados_costos_indirectos = sum(
            [1 for costo in costos_indirectos if self.es_instancia_costos_completa(costo)])

        # Verificar EvolucionGastoAsociado y CostoAnio
        fluctuacion_gasto = FluctuacionPresupuestaria.objects.filter(formulario_gore=self.formulario_gore)
        total_fluctuacion_gasto = fluctuacion_gasto.count()
        completados_fluctuacion_gasto = sum(
            1 for fluctuacion in fluctuacion_gasto if self.es_fluctuacion_completa(fluctuacion))

        # Total de campos y completados se ajusta para incluir el número de instancias
        total_campos = ( total_costos_directos + total_costos_indirectos +
                        total_fluctuacion_gasto)
        completados = (completados_costos_directos + completados_costos_indirectos +
                       completados_fluctuacion_gasto)

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
