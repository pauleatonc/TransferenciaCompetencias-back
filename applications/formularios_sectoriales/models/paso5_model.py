import os
from django.core.validators import FileExtensionValidator
from django.db.models import Sum

from . import EtapasEjercicioCompetencia
from .base_model import PasoBase, FormularioSectorial
from django.db import models, transaction

from ..functions import organigrama_regional_path
from applications.base.models import BaseModel
from applications.base.functions import validate_file_size_twenty
from ...regioncomuna.models import Region


class Paso5(PasoBase):

    @property
    def nombre_paso(self):
        return 'Costeo de la Competencia'

    @property
    def numero_paso(self):
        return 5

    def es_instancia_costos_completa(self, instancia):
        campos_requeridos = [
            'formulario_sectorial', 'item_subtitulo', 'total_anual', 'descripcion'
        ]
        return all(getattr(instancia, campo, None) for campo in campos_requeridos)

    def es_evolucion_gasto_completa(self, instancia):
        return all([
            instancia.subtitulo_id,
            CostoAnio.objects.filter(evolucion_gasto=instancia).exists()
        ]) and all(
            getattr(anio, 'costo', None) is not None
            for anio in CostoAnio.objects.filter(evolucion_gasto=instancia)
        )

    def es_variacion_promedio_completa(self, instancia):
        return bool(instancia.descripcion)

    def es_personal_directo_completo(self):
        return PersonalDirecto.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            estamento__isnull=False,
            calidad_juridica__isnull=False,
            renta_bruta__isnull=False
        ).exists()

    def es_personal_indirecto_completo(self):
        return PersonalIndirecto.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            estamento__isnull=False,
            calidad_juridica__isnull=False,
            numero_personas__isnull=False,
            renta_bruta__isnull=False
        ).exists()

    def avance(self):
        # Lista de todos los campos obligatorios del modelo Paso5
        campos_obligatorios_paso5 = [
            'descripcion_funciones_personal_directo', 'descripcion_funciones_personal_indirecto',
        ]
        total_campos_paso5 = len(campos_obligatorios_paso5)
        completados_paso5 = sum([1 for campo in campos_obligatorios_paso5 if getattr(self, campo, None)])

        # Verifica instancias de CostosDirectos y CostosIndirectos
        total_costos_directos = CostosDirectos.objects.filter(
            formulario_sectorial_id=self.formulario_sectorial_id).count()
        completados_costos_directos = sum(
            [1 for costo in CostosDirectos.objects.filter(formulario_sectorial_id=self.formulario_sectorial_id) if
             self.es_instancia_costos_completa(costo)])

        total_costos_indirectos = CostosIndirectos.objects.filter(
            formulario_sectorial_id=self.formulario_sectorial_id).count()
        completados_costos_indirectos = sum(
            [1 for costo in CostosIndirectos.objects.filter(formulario_sectorial_id=self.formulario_sectorial_id) if
             self.es_instancia_costos_completa(costo)])

        # Verificar EvolucionGastoAsociado y CostoAnio
        completados_evolucion_gasto = sum(
            1 for evolucion in EvolucionGastoAsociado.objects.filter(formulario_sectorial=self.formulario_sectorial)
            if self.es_evolucion_gasto_completa(evolucion)
        )
        total_evolucion_gasto = EvolucionGastoAsociado.objects.filter(
            formulario_sectorial=self.formulario_sectorial).count()

        # Verificar VariacionPromedio
        completados_variacion_promedio = sum(
            1 for variacion in VariacionPromedio.objects.filter(formulario_sectorial=self.formulario_sectorial)
            if self.es_variacion_promedio_completa(variacion)
        )
        total_variacion_promedio = VariacionPromedio.objects.filter(
            formulario_sectorial=self.formulario_sectorial).count()

        # Verificar PersonalDirecto y PersonalIndirecto
        completado_personal_directo = 1 if self.es_personal_directo_completo() else 0
        completado_personal_indirecto = 1 if self.es_personal_indirecto_completo() else 0

        # Total de campos y completados
        total_campos = 8
        completados = completados_paso5 + completados_costos_directos + completados_costos_indirectos + completados_evolucion_gasto + completados_variacion_promedio + completado_personal_directo + completado_personal_indirecto

        return f"{completados}/{total_campos}"

    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='paso5')

    """5.1 Costos asociados al ejercicio de la competencia"""
    total_costos_directos = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    total_costos_indirectos = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    costos_totales = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    """5.2 Costos asociados al ejercicio de la competencia"""
    glosas_especificas = models.TextField(max_length=500, blank=True)

    """5.3 Costos asociados al ejercicio de la competencia"""
    descripcion_funciones_personal_directo = models.TextField(max_length=1100, blank=True)
    descripcion_funciones_personal_indirecto = models.TextField(max_length=1100, blank=True)

    def save(self, *args, **kwargs):
        if self.campos_obligatorios_completados:
            self.completado = True
        else:
            self.completado = False
        super(Paso5, self).save(*args, **kwargs)


class Subtitulos(models.Model):
    subtitulo = models.CharField(max_length=10, unique=True)

    @property
    def nombre_item(self):
        return self.subtitulo


class ItemSubtitulo(models.Model):
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='items')
    item = models.CharField(max_length=100, unique=True)

    @property
    def nombre_item(self):
        return self.item


class CostosDirectos(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_a_costos_directos')
    etapa = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='costos_directos', blank=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_directos')
    total_anual = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    es_transversal = models.BooleanField(default=False, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actualizar_resumen_costos()
        self.crear_o_actualizar_resumen_evolucion_variacion()
        ResumenCostosPorSubtitulo.actualizar_total_anual(self.item_subtitulo.subtitulo_id, self.formulario_sectorial_id)
        EvolucionGastoAsociado.actualizar_evolucion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                                  self.formulario_sectorial_id)
        VariacionPromedio.actualizar_variacion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                             self.formulario_sectorial_id)

    def delete(self, *args, **kwargs):
        subtitulo_id = self.item_subtitulo.subtitulo_id
        formulario_sectorial_id = self.formulario_sectorial_id
        super().delete(*args, **kwargs)
        self.actualizar_resumen_costos()
        ResumenCostosPorSubtitulo.actualizar_total_anual(subtitulo_id, formulario_sectorial_id)
        EvolucionGastoAsociado.actualizar_evolucion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                                  self.formulario_sectorial_id)
        VariacionPromedio.actualizar_variacion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                             self.formulario_sectorial_id)

    def actualizar_resumen_costos(self):
        total = CostosDirectos.objects.filter(formulario_sectorial_id=self.formulario_sectorial_id).aggregate(
            Sum('total_anual'))['total_anual__sum'] or 0
        paso = Paso5.objects.get(formulario_sectorial_id=self.formulario_sectorial_id)
        paso.total_costos_directos = total
        paso.save()

    def crear_o_actualizar_resumen_evolucion_variacion(self):
        subtitulo_id = self.item_subtitulo.subtitulo_id
        total_directos = CostosDirectos.objects.filter(item_subtitulo__subtitulo_id=subtitulo_id,
                                                       formulario_sectorial_id=self.formulario_sectorial_id).aggregate(
            Sum('total_anual'))['total_anual__sum'] or 0


class CostosIndirectos(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_b_costos_indirectos')
    etapa = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='costos_indirectos')
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_indirectos')
    total_anual = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    es_transversal = models.BooleanField(default=False, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actualizar_resumen_costos()
        self.crear_o_actualizar_resumen_evolucion_variacion()
        ResumenCostosPorSubtitulo.actualizar_total_anual(self.item_subtitulo.subtitulo_id, self.formulario_sectorial_id)
        EvolucionGastoAsociado.actualizar_evolucion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                                  self.formulario_sectorial_id)
        VariacionPromedio.actualizar_variacion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                             self.formulario_sectorial_id)

    def delete(self, *args, **kwargs):
        subtitulo_id = self.item_subtitulo.subtitulo_id
        formulario_sectorial_id = self.formulario_sectorial_id
        super().delete(*args, **kwargs)
        self.actualizar_resumen_costos()
        ResumenCostosPorSubtitulo.actualizar_total_anual(subtitulo_id, formulario_sectorial_id)
        EvolucionGastoAsociado.actualizar_evolucion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                                  self.formulario_sectorial_id)
        VariacionPromedio.actualizar_variacion_por_subtitulo(self.item_subtitulo.subtitulo_id,
                                                             self.formulario_sectorial_id)

    def actualizar_resumen_costos(self):
        total = CostosIndirectos.objects.filter(formulario_sectorial_id=self.formulario_sectorial_id).aggregate(
            Sum('total_anual'))['total_anual__sum'] or 0
        paso = Paso5.objects.get(formulario_sectorial_id=self.formulario_sectorial_id)
        paso.total_costos_indirectos = total
        paso.save()

    def crear_o_actualizar_resumen_evolucion_variacion(self):
        subtitulo_id = self.item_subtitulo.subtitulo_id
        total_directos = CostosIndirectos.objects.filter(item_subtitulo__subtitulo_id=subtitulo_id,
                                                         formulario_sectorial_id=self.formulario_sectorial_id).aggregate(
            Sum('total_anual'))['total_anual__sum'] or 0


class ResumenCostosPorSubtitulo(BaseModel):
    """Modelo para almacenar el resumen de costos por subtitulo."""
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_c_resumen_costos_por_subtitulo')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='resumen_costos')
    total_anual = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    descripcion = models.TextField(max_length=300, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actualizar_resumen_costos()

    def actualizar_resumen_costos(self):
        total = \
        ResumenCostosPorSubtitulo.objects.filter(formulario_sectorial_id=self.formulario_sectorial_id).aggregate(
            Sum('total_anual'))[
            'total_anual__sum'] or 0
        paso = Paso5.objects.get(formulario_sectorial_id=self.formulario_sectorial_id)
        paso.costos_totales = total
        paso.save()

    @classmethod
    def actualizar_total_anual(cls, subtitulo_id, formulario_sectorial_id):
        total_directos = CostosDirectos.objects.filter(
            item_subtitulo__subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).aggregate(Sum('total_anual'))['total_anual__sum'] or 0

        total_indirectos = CostosIndirectos.objects.filter(
            item_subtitulo__subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).aggregate(Sum('total_anual'))['total_anual__sum'] or 0

        total = total_directos + total_indirectos

        if total > 0:
            resumen, created = cls.objects.get_or_create(
                subtitulo_id=subtitulo_id,
                formulario_sectorial_id=formulario_sectorial_id,
                defaults={'total_anual': total}
            )
            if not created:
                resumen.total_anual = total
                resumen.save()
        else:
            cls.objects.filter(subtitulo_id=subtitulo_id, formulario_sectorial_id=formulario_sectorial_id).delete()

    def __str__(self):
        return f"{self.subtitulo.subtitulo} - Total Anual: {self.total_anual}"


class EvolucionGastoAsociado(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_2_evolucion_gasto_asociado')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='evolucion_gasto_asociado')
    descripcion = models.TextField(max_length=500, blank=True)

    @classmethod
    def actualizar_evolucion_por_subtitulo(cls, subtitulo_id, formulario_sectorial_id):
        total_directos = CostosDirectos.objects.filter(
            item_subtitulo__subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).aggregate(Sum('total_anual'))['total_anual__sum'] or 0

        total_indirectos = CostosIndirectos.objects.filter(
            item_subtitulo__subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).aggregate(Sum('total_anual'))['total_anual__sum'] or 0

        total = total_directos + total_indirectos

        if total > 0:
            evolucion, created = cls.objects.get_or_create(
                subtitulo_id=subtitulo_id,
                formulario_sectorial_id=formulario_sectorial_id,
            )
            if not created:
                evolucion.save()
        else:
            cls.objects.filter(subtitulo_id=subtitulo_id, formulario_sectorial_id=formulario_sectorial_id).delete()


class CostoAnio(BaseModel):
    evolucion_gasto = models.ForeignKey(EvolucionGastoAsociado, on_delete=models.CASCADE, related_name='costo_anio')
    anio = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)


class VariacionPromedio(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_2_variacion_promedio')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='variacion_promedio')
    gasto_n_5 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    gasto_n_1 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    variacion = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)

    @classmethod
    def actualizar_variacion_por_subtitulo(cls, subtitulo_id, formulario_sectorial_id):
        total_directos = CostosDirectos.objects.filter(
            item_subtitulo__subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).aggregate(Sum('total_anual'))['total_anual__sum'] or 0

        total_indirectos = CostosIndirectos.objects.filter(
            item_subtitulo__subtitulo_id=subtitulo_id,
            formulario_sectorial_id=formulario_sectorial_id
        ).aggregate(Sum('total_anual'))['total_anual__sum'] or 0

        total = total_directos + total_indirectos

        if total > 0:
            variacion, created = cls.objects.get_or_create(
                subtitulo_id=subtitulo_id,
                formulario_sectorial_id=formulario_sectorial_id,
            )
            if not created:
                variacion.save()
        else:
            cls.objects.filter(subtitulo_id=subtitulo_id, formulario_sectorial_id=formulario_sectorial_id).delete()

    def calcular_variacion(self):
        self.variacion = (self.gasto_n_5 or 0) - (self.gasto_n_1 or 0)
        self.save()


class Estamento(models.Model):
    estamento = models.CharField(max_length=100)


class CalidadJuridica(models.Model):
    calidad_juridica = models.CharField(max_length=100)


class PersonalDirecto(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_3_a_personal_directo')
    estamento = models.ForeignKey(Estamento, on_delete=models.CASCADE, related_name='personal_directo')
    calidad_juridica = models.ForeignKey(CalidadJuridica, on_delete=models.CASCADE, related_name='personal_directo')
    renta_bruta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    grado = models.IntegerField(null=True, blank=True)


class PersonalIndirecto(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_3_b_personal_indirecto')
    estamento = models.ForeignKey(Estamento, on_delete=models.CASCADE, related_name='personal_indirecto')
    calidad_juridica = models.ForeignKey(CalidadJuridica, on_delete=models.CASCADE, related_name='personal_indirecto')
    numero_personas = models.IntegerField(null=True, blank=True)
    renta_bruta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    grado = models.IntegerField(null=True, blank=True)
