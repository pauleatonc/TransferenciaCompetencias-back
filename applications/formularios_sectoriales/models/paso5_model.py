from django.db import models
from django.db.models import Sum

from applications.base.models import BaseModel
from applications.regioncomuna.models import Region
from . import EtapasEjercicioCompetencia
from .base_model import PasoBase, FormularioSectorial


class Paso5Encabezado(PasoBase):
    formulario_sectorial = models.OneToOneField(FormularioSectorial, on_delete=models.CASCADE, related_name='paso5encabezado', null=True, blank=True)

    @property
    def nombre_paso(self):
        return 'Costeo de la Competencia'

    @property
    def numero_paso(self):
        return 5

    def avance_numerico(self):
        pasos5 = Paso5.objects.filter(formulario_sectorial=self.formulario_sectorial)
        total_pasos = pasos5.count()
        pasos_completos = 0
        for paso in pasos5:
            avance = paso.avance().split('/')
            if avance[1] != '0':  # Asegura que no estamos tratando con un avance 0/0
                if avance[0] == avance[1]:
                    pasos_completos += 1
        return pasos_completos, total_pasos

    def avance(self):
        pasos_completos, total_pasos = self.avance_numerico()
        return f"{pasos_completos}/{total_pasos}"

    @property
    def multiplicador_caracteres_region(self):
        # Accede a las regiones asociadas a la competencia a través del formulario sectorial
        competencia = self.formulario_sectorial.competencia
        numero_regiones = competencia.regiones.count()

        if numero_regiones == 1:
            return 500
        else:
            return 300 + numero_regiones * 200


class Paso5(PasoBase):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE, related_name='paso5')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='paso5', null=True, blank=True)

    """5.1 Costos asociados al ejercicio de la competencia"""
    total_costos_directos = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    total_costos_indirectos = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    costos_totales = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    descripcion_costos_totales = models.TextField(max_length=300, blank=True)

    """5.2 Costos asociados al ejercicio de la competencia"""
    glosas_especificas = models.TextField(max_length=1100, blank=True)

    """5.3 Costos asociados al ejercicio de la competencia"""
    descripcion_funciones_personal_directo = models.TextField(max_length=1100, blank=True)
    descripcion_funciones_personal_indirecto = models.TextField(max_length=1100, blank=True)
    """5.3a Costos Directos asociados al ejercicio de la competencia"""
    sub21_total_personal_planta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_personal_planta_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_personal_planta_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_total_personal_contrata = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_personal_contrata_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_personal_contrata_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_total_otras_remuneraciones = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_otras_remuneraciones_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_otras_remuneraciones_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_total_gastos_en_personal = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_gastos_en_personal_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21_gastos_en_personal_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    """5.3b Costos Indirectos asociados al ejercicio de la competencia"""
    sub21b_total_personal_planta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_planta_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_planta_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_total_personal_contrata = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_contrata_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_contrata_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_total_otras_remuneraciones = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_otras_remuneraciones_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_otras_remuneraciones_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_total_gastos_en_personal = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_gastos_en_personal_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_gastos_en_personal_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    def es_instancia_costos_completa(self, instancia):
        campos_requeridos = ['item_subtitulo', 'total_anual', 'es_transversal', 'descripcion']
        return all(getattr(instancia, campo, None) is not None for campo in campos_requeridos[:-1]) and bool(instancia.descripcion.strip())

    def es_personal_directo_completo(self, personal):
        return personal.estamento is not None and personal.renta_bruta is not None

    def es_personal_indirecto_completo(self, personal):
        return personal.estamento is not None and personal.numero_personas is not None and personal.renta_bruta is not None

    def verificar_costos_especiales(self, costos):
        # Esta función verifica si hay costos especiales y devuelve True si existen
        return costos.filter(item_subtitulo__item="04 - Otros Gastos en Personal").exists()

    def avance_numerico(self):
        completados = 0
        total_campos = 4  # Comienza con 4 campos base para verificar

        costos_directos = self.formulario_sectorial.p_5_1_a_costos_directos.filter(region=self.region)
        costos_indirectos = self.formulario_sectorial.p_5_1_b_costos_indirectos.filter(region=self.region)
        personal_directo = self.formulario_sectorial.p_5_3_a_personal_directo.filter(region=self.region)
        personal_indirecto = self.formulario_sectorial.p_5_3_b_personal_indirecto.filter(region=self.region)

        # Conteo de costos
        if costos_directos.exists() and costos_indirectos.exists():
            total_campos += 1  # Incrementa si ambos costos existen
            if self.verificar_costos_especiales(costos_directos) or self.verificar_costos_especiales(costos_indirectos):
                total_campos += 1  # Incrementa si existen costos especiales
        total_campos = min(total_campos, 6)  # Asegura que no exceda 6

        # Conteo de personal
        if personal_directo.exists() and personal_indirecto.exists():
            total_campos += 1

        total_campos = min(total_campos, 6)  # Asegura que no exceda 6

        # Completados
        if all(self.es_instancia_costos_completa(costo) for costo in costos_directos) and costos_directos.exists():
            completados += 1

        if all(self.es_instancia_costos_completa(costo) for costo in costos_indirectos) and costos_indirectos.exists():
            completados += 1

        if all(self.es_personal_directo_completo(personal) for personal in
               personal_directo) and personal_directo.exists():
            completados += 1

        if all(self.es_personal_indirecto_completo(personal) for personal in
               personal_indirecto) and personal_indirecto.exists():
            completados += 1

        # Verificar cada CostoAnio para cada EvolucionGasto
        evolucion_gastos = self.formulario_sectorial.p_5_2_evolucion_gasto_asociado.filter(region=self.region)
        if evolucion_gastos.exists():
            completados_evolucion_gasto = all(
                costo_anio.costo is not None
                for evolucion in evolucion_gastos
                for costo_anio in evolucion.costo_anio.all()
            )
            if completados_evolucion_gasto:
                completados += 1

        # Verificar cada VariacionPromedio
        variaciones_promedio = self.formulario_sectorial.p_5_2_variacion_promedio.filter(region=self.region)
        if variaciones_promedio.exists():
            completados_variacion_promedio = all(
                variacion.descripcion.strip()
                for variacion in variaciones_promedio
            )
            if completados_variacion_promedio:
                completados += 1

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"


class Subtitulos(models.Model):
    """ Para poblar la base de datos se debe correr el comando python manage.py populate_from_excel"""
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
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='costos_directos', null=True, blank=True)
    etapa = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='costos_directos', blank=True)
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='costos_directos', blank=True, null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_directos', blank=True, null=True)
    total_anual = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    es_transversal = models.BooleanField(blank=True, null=True, default=None)
    descripcion = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['created_date']

    @property
    def personal_related_model(self):
        return PersonalDirecto


class CostosIndirectos(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_b_costos_indirectos')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='costos_indirectos', null=True, blank=True)
    etapa = models.ManyToManyField(EtapasEjercicioCompetencia, related_name='costos_indirectos')
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='costos_indirectos', blank=True, null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='costos_indirectos', blank=True, null=True)
    total_anual = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    es_transversal = models.BooleanField(blank=True, null=True, default=None)
    descripcion = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['created_date']

    @property
    def personal_related_model(self):
        return PersonalIndirecto


class ResumenCostosPorSubtitulo(BaseModel):
    """Modelo para almacenar el resumen de costos por subtitulo."""
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_1_c_resumen_costos_por_subtitulo')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='resumen_costos', null=True, blank=True)
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='resumen_costos')
    total_anual = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    descripcion = models.TextField(max_length=300, blank=True)

    class Meta:
        ordering = ['subtitulo']


class EvolucionGastoAsociado(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_2_evolucion_gasto_asociado')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='evolucion_gasto_asociado', null=True, blank=True)
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='evolucion_gasto_asociado')
    descripcion = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['subtitulo']


class CostoAnio(BaseModel):
    evolucion_gasto = models.ForeignKey(EvolucionGastoAsociado, on_delete=models.CASCADE, related_name='costo_anio')
    anio = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    class Meta:
        ordering = ['anio']


class VariacionPromedio(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_2_variacion_promedio')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='variacion_promedio', null=True, blank=True)
    subtitulo = models.ForeignKey(Subtitulos, on_delete=models.CASCADE, related_name='variacion_promedio')
    variacion_gasto_n_5 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    variacion_gasto_n_4 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    variacion_gasto_n_3 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    variacion_gasto_n_2 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    descripcion = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['subtitulo']


class Estamento(models.Model):
    estamento = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class CalidadJuridica(models.Model):
    calidad_juridica = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class PersonalDirecto(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_3_a_personal_directo')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='personal_directo', null=True, blank=True)
    costos = models.ForeignKey(CostosDirectos, on_delete=models.CASCADE, related_name='personal_directo', null=True, blank=True)
    estamento = models.ForeignKey(Estamento, on_delete=models.CASCADE, related_name='personal_directo', null=True, blank=True)
    calidad_juridica = models.ForeignKey(CalidadJuridica, on_delete=models.CASCADE, related_name='personal_directo', null=True, blank=True)
    renta_bruta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    grado = models.IntegerField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['created_date']


class PersonalIndirecto(BaseModel):
    formulario_sectorial = models.ForeignKey(FormularioSectorial, on_delete=models.CASCADE,
                                             related_name='p_5_3_b_personal_indirecto')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='personal_indirecto', null=True, blank=True)
    costos = models.ForeignKey(CostosIndirectos, on_delete=models.CASCADE, related_name='personal_indirecto', null=True, blank=True)
    estamento = models.ForeignKey(Estamento, on_delete=models.CASCADE, related_name='personal_indirecto', null=True, blank=True)
    calidad_juridica = models.ForeignKey(CalidadJuridica, on_delete=models.CASCADE, related_name='personal_indirecto', null=True, blank=True)
    numero_personas = models.IntegerField(null=True, blank=True)
    renta_bruta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    total_rentas = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    grado = models.IntegerField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['created_date']

    def save(self, *args, **kwargs):
        if self.renta_bruta is not None and self.numero_personas is not None:
            self.total_rentas = self.renta_bruta * self.numero_personas
        else:
            self.total_rentas = None
        super().save(*args, **kwargs)
