from django.db import models

from applications.base.models import BaseModel
from applications.formularios_sectoriales.models import (
    ItemSubtitulo,
    Estamento,
    CalidadJuridica
)
from applications.sectores_gubernamentales.models import SectorGubernamental
from .base_model import PasoBase, FormularioGORE


class Paso3(PasoBase):
    @property
    def nombre_paso(self):
        return 'Incidencia en la capacidad administrativa'

    @property
    def numero_paso(self):
        return 3

    def es_personal_directo_completo(self):
        return PersonalDirectoGORE.objects.filter(
            formulario_gore=self.formulario_gore,
            estamento__isnull=False,
            renta_bruta__isnull=False
        ).exists()

    def es_personal_indirecto_completo(self):
        return PersonalIndirectoGORE.objects.filter(
            formulario_gore=self.formulario_gore,
            estamento__isnull=False,
            numero_personas_gore__isnull=False,
            renta_bruta__isnull=False
        ).exists()

    def es_sistema_informatico_completo(self):
        return SistemasInformaticos.objects.filter(
            formulario_gore=self.formulario_gore,
            nombre_plataforma__isnull=False,
            descripcion_tecnica__isnull=False,
            costo__isnull=False,
            funcion__isnull=False
        ).exists()

    def es_recursos_completo(self):
        return RecursosFisicosInfraestructura.objects.filter(
            formulario_gore=self.formulario_gore,
            costo_unitario__isnull=False,
            cantidad__isnull=False,
            fundamentacion__isnull=False
        ).exists()

    def avance_numerico(self):
        # Lista de todos los campos obligatorios del modelo Paso5
        campos_obligatorios_paso5 = [
            'descripcion_perfiles_tecnicos_directo', 'descripcion_perfiles_tecnicos_indirecto',
        ]
        total_campos_paso5 = len(campos_obligatorios_paso5)
        completados_paso5 = sum([1 for campo in campos_obligatorios_paso5 if getattr(self, campo, None)])

        # Verificar PersonalDirecto, PersonalIndirecto,  SistemasInformaticos y RecursosFisicosInfraestructura
        # (estos cuentan como un campo cada uno, sin importar la cantidad de instancias)
        completado_personal_directo = 1 if self.es_personal_directo_completo() else 0
        completado_personal_indirecto = 1 if self.es_personal_indirecto_completo() else 0
        completado_sistema_informatico = 1 if self.es_sistema_informatico_completo() else 0
        completado_recursos = 1 if self.es_recursos_completo() else 0

        # Total de campos y completados se ajusta para incluir el número de instancias
        total_campos = (total_campos_paso5 + 4)
        completados = (completados_paso5 + completado_personal_directo + completado_personal_indirecto +
                       completado_sistema_informatico + completado_recursos)

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"

    formulario_gore = models.OneToOneField(FormularioGORE, on_delete=models.CASCADE, related_name='paso3_gore')

    """3.1 Estamento, tipo de contrato y cantidad de personal para el Gobierno Regional solicitante"""
    descripcion_perfiles_tecnicos_directo = models.TextField(max_length=1100, blank=True)
    descripcion_perfiles_tecnicos_indirecto = models.TextField(max_length=1100, blank=True)

    """3.1a Costos Personal Directo asociados al ejercicio de la competencia"""
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

    """3.1b Costos Personal Indirecto asociados al ejercicio de la competencia"""
    sub21b_total_personal_planta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_planta_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_planta_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_total_personal_contrata = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_contrata_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_personal_contrata_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_total_otras_remuneraciones = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_otras_remuneraciones_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True,
                                                                  blank=True)
    sub21b_otras_remuneraciones_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_total_gastos_en_personal = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_gastos_en_personal_justificado = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    sub21b_gastos_en_personal_justificar = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    subtitulo_21_informados_gore = models.IntegerField(null=True, blank=True)
    subtitulo_21_justificados_gore = models.IntegerField(null=True, blank=True)
    subtitulo_21_por_justificar = models.IntegerField(null=True, blank=True)

    '''3.2 Resumen costos GORE'''
    subtitulo_22_diferencia_sector = models.IntegerField(null=True, blank=True)
    subtitulo_22_justificados_gore = models.IntegerField(null=True, blank=True)
    subtitulo_22_por_justificar = models.IntegerField(null=True, blank=True)

    subtitulo_29_diferencia_sector = models.IntegerField(null=True, blank=True)
    subtitulo_29_justificados_gore = models.IntegerField(null=True, blank=True)
    subtitulo_29_por_justificar = models.IntegerField(null=True, blank=True)

    costos_informados_gore = models.IntegerField(null=True, blank=True)
    costos_justificados_gore = models.IntegerField(null=True, blank=True)
    costos_justificar_gore = models.IntegerField(null=True, blank=True)

    def calcular_por_justificar(self, diferencia_sector, justificados_gore):
        """
        Calcula el valor por justificar basado en la diferencia_sector y los justificados_gore.
        Retorna None si cualquiera de los valores no está definido.
        """
        if diferencia_sector is not None and justificados_gore is not None:
            return diferencia_sector - justificados_gore
        return None

    def save(self, *args, **kwargs):
        # Calcula 'por justificar' para el subtitulo 21
        self.subtitulo_21_por_justificar = self.calcular_por_justificar(
            self.subtitulo_21_informados_gore,
            self.subtitulo_21_justificados_gore
        )

        # Calcula 'por justificar' para el subtitulo 22
        self.subtitulo_22_por_justificar = self.calcular_por_justificar(
            self.subtitulo_22_diferencia_sector,
            self.subtitulo_22_justificados_gore
        )

        # Calcula 'por justificar' para el subtitulo 29
        self.subtitulo_29_por_justificar = self.calcular_por_justificar(
            self.subtitulo_29_diferencia_sector,
            self.subtitulo_29_justificados_gore
        )

        # Suma de valores informados y justificados, considerando None como 0
        valores_informados = [
            self.subtitulo_21_informados_gore or 0,
            self.subtitulo_22_diferencia_sector or 0,
            self.subtitulo_29_diferencia_sector or 0
        ]
        valores_justificados = [
            self.subtitulo_21_justificados_gore or 0,
            self.subtitulo_22_justificados_gore or 0,
            self.subtitulo_29_justificados_gore or 0
        ]

        self.costos_informados_gore = sum(valores_informados)
        self.costos_justificados_gore = sum(valores_justificados)

        # Cálculo de costos por justificar como la resta de informados y justificados
        self.costos_justificar_gore = self.costos_informados_gore - self.costos_justificados_gore

        super().save(*args, **kwargs)


class PersonalDirectoGORE(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_3_1_a_personal_directo')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='personal_directo_gore',
                               blank=True, null=True)
    estamento = models.ForeignKey(Estamento, on_delete=models.CASCADE, related_name='personal_directo_gore', null=True, blank=True)
    calidad_juridica = models.ForeignKey(CalidadJuridica, on_delete=models.CASCADE, related_name='personal_directo_gore', null=True, blank=True)
    renta_bruta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    grado = models.CharField(max_length=10, null=True, blank=True, default=None)
    comision_servicio = models.BooleanField(blank=True, null=True, default=False)
    utilizara_recurso = models.BooleanField(blank=True, null=True, default=None)
    id_sectorial = models.IntegerField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['created_date']


class PersonalIndirectoGORE(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_3_1_b_personal_indirecto')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='personal_indirecto_gore',
                               blank=True, null=True)
    estamento = models.ForeignKey(Estamento, on_delete=models.CASCADE, related_name='personal_indirecto_gore', null=True, blank=True)
    calidad_juridica = models.ForeignKey(CalidadJuridica, on_delete=models.CASCADE, related_name='personal_indirecto_gore', null=True, blank=True)
    numero_personas_sectorial = models.IntegerField(null=True, blank=True)
    numero_personas_gore = models.IntegerField(null=True, blank=True)
    renta_bruta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    total_rentas = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    grado = models.CharField(max_length=10, null=True, blank=True, default=None)
    comision_servicio = models.BooleanField(blank=True, null=True, default=False)
    utilizara_recurso = models.BooleanField(blank=True, null=True, default=None)
    id_sectorial = models.IntegerField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['created_date']

    def save(self, *args, **kwargs):
        if self.renta_bruta is not None and self.numero_personas_gore is not None:
            self.total_rentas = self.renta_bruta * self.numero_personas_gore
        else:
            self.total_rentas = None
        super().save(*args, **kwargs)


class RecursosComparados(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_3_2_recursos_comparados')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='recursos_comparados_gore',
                               blank=True, null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='recursos_comparados_gore',
                                       blank=True, null=True)
    costo_sector = models.IntegerField(null=True, blank=True, default=None)
    costo_gore = models.IntegerField(null=True, blank=True, default=None)
    diferencia_monto = models.IntegerField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['sector', 'item_subtitulo__subtitulo', 'item_subtitulo']


class SistemasInformaticos(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_3_2_a_sistemas_informaticos')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='sistemas_informaticos_gore',
                               blank=True, null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='sistemas_informaticos_gore', null=True, blank=True)
    nombre_plataforma = models.TextField(max_length=500, blank=True)
    descripcion_tecnica = models.TextField(max_length=500, blank=True)
    costo = models.IntegerField(null=True, blank=True, default=None)
    funcion = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['created_date']


class RecursosFisicosInfraestructura(BaseModel):
    formulario_gore = models.ForeignKey(FormularioGORE, on_delete=models.CASCADE,
                                             related_name='p_3_2_b_recursos_fisicos_infraestructura')
    sector = models.ForeignKey(SectorGubernamental, on_delete=models.CASCADE, related_name='recursos_fisicos_infraestructura_gore',
                               blank=True, null=True)
    item_subtitulo = models.ForeignKey(ItemSubtitulo, on_delete=models.CASCADE, related_name='recursos_fisicos_infraestructura_gore', null=True, blank=True)
    costo_unitario = models.IntegerField(null=True, blank=True, default=None)
    cantidad = models.IntegerField(null=True, blank=True, default=None)
    costo_total = models.IntegerField(null=True, blank=True, default=None)
    fundamentacion = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        if self.costo_total is not None and self.cantidad is not None:
            self.costo_unitario = self.costo_total / self.cantidad
        else:
            self.costo_total = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_date']

