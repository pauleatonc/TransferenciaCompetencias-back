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
        pasos_completos = sum(1 for paso in pasos5 if paso.avance().split('/')[0] == paso.avance().split('/')[1])
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
        # Revisar los campos básicos requeridos
        campos_requeridos = ['item_subtitulo', 'total_anual', 'es_transversal', 'descripcion']
        campos_completos = all(getattr(instancia, campo, None) is not None for campo in
                               campos_requeridos[:3])  # Primero verificamos los campos que no son de tipo texto

        # Verificar que el campo 'descripcion' no solo exista sino que tenga contenido relevante (no esté vacío ni solo espacios)
        descripcion_completa = bool(getattr(instancia, 'descripcion', '').strip())

        # Todos los campos deben estar completos para considerar la instancia completa
        return campos_completos and descripcion_completa

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
            region=self.region,
            estamento__isnull=False,
            renta_bruta__isnull=False
        ).exists()

    def es_personal_indirecto_completo(self):
        return PersonalIndirecto.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            region=self.region,
            estamento__isnull=False,
            numero_personas__isnull=False,
            renta_bruta__isnull=False
        ).exists()

    def avance_numerico(self):
        # Queries y conteos de instancias para costos directos e indirectos
        costos_directos = CostosDirectos.objects.filter(
            formulario_sectorial_id=self.formulario_sectorial_id,
            region=self.region
        )
        total_costos_directos = costos_directos.count()
        completados_costos_directos = sum(1 for costo in costos_directos if self.es_instancia_costos_completa(costo))

        costos_indirectos = CostosIndirectos.objects.filter(
            formulario_sectorial_id=self.formulario_sectorial_id,
            region=self.region
        )
        total_costos_indirectos = costos_indirectos.count()
        completados_costos_indirectos = sum(
            1 for costo in costos_indirectos if self.es_instancia_costos_completa(costo))

        # Queries y conteos para evolución de gasto y variación promedio
        evolucion_gasto = EvolucionGastoAsociado.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            region=self.region
        )
        total_evolucion_gasto = evolucion_gasto.count()
        completados_evolucion_gasto = sum(
            1 for evolucion in evolucion_gasto if self.es_evolucion_gasto_completa(evolucion))

        variacion_promedio = VariacionPromedio.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            region=self.region
        )
        total_variacion_promedio = variacion_promedio.count()
        completados_variacion_promedio = sum(
            1 for variacion in variacion_promedio if self.es_variacion_promedio_completa(variacion))

        # Queries y conteos para personal directo e indirecto
        personal_directo = PersonalDirecto.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            region=self.region
        )
        total_personal_directo = personal_directo.count()
        completado_personal_directo = sum(1 for personal in personal_directo if self.es_personal_directo_completo())

        personal_indirecto = PersonalIndirecto.objects.filter(
            formulario_sectorial=self.formulario_sectorial,
            region=self.region
        )
        total_personal_indirecto = personal_indirecto.count()
        completado_personal_indirecto = sum(
            1 for personal in personal_indirecto if self.es_personal_indirecto_completo())

        # Descripciones de personal
        total_campos = (total_costos_directos + total_costos_indirectos +
                        total_evolucion_gasto + total_variacion_promedio +
                        total_personal_directo + total_personal_indirecto)
        completados = (completados_costos_directos + completados_costos_indirectos +
                       completados_evolucion_gasto + completados_variacion_promedio +
                       completado_personal_directo + completado_personal_indirecto)

        # Incluir descripciones si hay personal directo o indirecto
        if total_personal_directo > 0:
            total_campos += 1
            if self.descripcion_funciones_personal_directo.strip():
                completados += 1

        if total_personal_indirecto > 0:
            total_campos += 1
            if self.descripcion_funciones_personal_indirecto.strip():
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
