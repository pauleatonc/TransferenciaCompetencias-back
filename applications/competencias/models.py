from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from applications.base.functions import validate_file_size_twenty, validate_file_size_five
from applications.base.models import BaseModel
from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental


#


class Ambito(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Competencia(BaseModel):
    ORIGEN = (
        ('OP', 'Oficio Presidencial'),
        ('SG', 'Solicitud GORE')
    )
    ESTADO = (
        ('EP', 'En Estudio'),
        ('FIN', 'Finalizada'),
        ('SU', 'Sin usuario sectorial')
    )
    MODALIDAD_EJERCICIO = (
        ('Exclusiva', 'Exclusiva'),
        ('Compartida', 'Compartida')
    )
    RECOMENDACION = (
        ('Pendiente', 'Pendiente'),
        ('Favorable', 'Favorable'),
        ('Desfavorable', 'Desfavorable'),
        ('Favorable parcial', 'Favorable parcial')
    )

    nombre = models.CharField(max_length=200, unique=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='competencia_creada',
        verbose_name='Creado por'
    )
    sectores = models.ManyToManyField(
        SectorGubernamental,
        blank=False,
        verbose_name='Sectores'
    )
    ambito_competencia = models.ForeignKey(Ambito, on_delete=models.CASCADE, related_name='ambito_competencia',
                                           null=True, blank=True)
    regiones = models.ManyToManyField(
        Region,
        blank=False,
        verbose_name='Regiones'
    )
    origen = models.CharField(max_length=5, choices=ORIGEN, default='OP')
    oficio_origen = models.FileField(upload_to='oficios_competencias',
                                     validators=[
                                         FileExtensionValidator(
                                             ['pdf'], message='Solo se permiten archivos PDF.'),
                                         validate_file_size_twenty],
                                     verbose_name='Oficio Origen Competencia', blank=True, null=True)

    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=5, choices=ESTADO, default='SU')
    plazo_formulario_sectorial = models.IntegerField(
        validators=[
            MinValueValidator(15),
            MaxValueValidator(30)
        ],
        help_text="El plazo debe estar entre 15 y 30 días."
    )
    plazo_formulario_gore = models.IntegerField(
        validators=[
            MinValueValidator(15),
            MaxValueValidator(30)
        ],
        help_text="El plazo debe estar entre 15 y 30 días."
    )
    usuarios_subdere = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_subdere',
        blank=True,
        limit_choices_to={'groups__name': 'SUBDERE'}
    )
    usuarios_dipres = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_dipres',
        blank=True,
        limit_choices_to={'groups__name': 'DIPRES'}
    )
    usuarios_sectoriales = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_sectoriales',
        blank=True,
        limit_choices_to=Q(groups__name='Usuario Sectorial')
    )
    usuarios_gore = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='competencias_gore',
        blank=True,
        limit_choices_to=Q(groups__name='GORE')
    )

    # Campos para revisión final SUBDERE
    ambito_definitivo_competencia = models.ForeignKey(Ambito, on_delete=models.CASCADE,
                                                      related_name='ambito_definitivo_competencia',
                                                      null=True, blank=True)
    regiones_recomendadas = models.ManyToManyField(
        Region,
        blank=True,
        related_name='regiones_recomendadas',
        verbose_name='Regiones recomendadas'
    )
    recursos_requeridos = models.TextField(blank=True, null=True)
    modalidad_ejercicio = models.CharField(max_length=20, choices=MODALIDAD_EJERCICIO, blank=True, null=True)
    implementacion_acompanamiento = models.TextField(blank=True, null=True)
    condiciones_ejercicio = models.TextField(blank=True, null=True)
    formulario_final_enviado = models.BooleanField(default=False)
    fecha_envio_formulario_final = models.DateTimeField(null=True, blank=True)
    recomendacion_transferencia = models.CharField(max_length=25, choices=RECOMENDACION, blank=True, null=True, default='Pendiente')
    imprimir_formulario_final = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Competencia'
        verbose_name_plural = 'Competencias'

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()

    def tiempo_transcurrido(self):
        """
        Calcula el tiempo transcurrido desde fecha_inicio hasta fecha_fin.
        Si fecha_fin no está asignada, usa el tiempo actual.
        Devuelve un diccionario con los días, horas y minutos transcurridos.
        """
        if not self.fecha_inicio:
            return {"dias": None, "horas": None, "minutos": None}

        fecha_fin = self.fecha_fin if self.fecha_fin else timezone.now()

        diferencia = fecha_fin - self.fecha_inicio
        dias = diferencia.days
        horas = diferencia.seconds // 3600
        minutos = (diferencia.seconds % 3600) // 60

        return {"dias": dias, "horas": horas, "minutos": minutos}


class DocumentosComplementarios(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    nombre_documento = models.CharField(max_length=100, unique=True)
    documento = models.FileField(upload_to='documentos_competencias',
                                 validators=[
                                     FileExtensionValidator(
                                         ['pdf'], message='Solo se permiten archivos PDF.'),
                                     validate_file_size_five],
                                 verbose_name='Documentos complementarios Competencia', blank=True, null=True)



# Modelos para revisión final SUBDERE
class RecomendacionesDesfavorables(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, related_name='recomendaciones_desfavorables')
    justificacion = models.TextField(max_length=500)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)


class Temporalidad(BaseModel):
    TEMPORALIDAD = (
        ('Definitiva', 'Definitiva'),
        ('Temporal', 'Temporal')
    )
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, related_name='temporalidad_gradualidad')
    region = models.ManyToManyField(Region, blank=True, related_name='regiones_temporalidad_gradualidad')
    temporalidad = models.CharField(max_length=10, choices=TEMPORALIDAD, blank=True, null=True)
    anios = models.IntegerField(blank=True, null=True)
    justificacion_temporalidad = models.TextField(max_length=500, blank=True, null=True)
    gradualidad_meses = models.IntegerField(blank=True, null=True)
    justificacion_gradualidad = models.TextField(max_length=500, blank=True, null=True)


class PasoBase(BaseModel):

    @property
    def completado(self):
        return self.campos_obligatorios_completados

    @property
    def campos_obligatorios_completados(self):
        completados, total_campos = self.avance_numerico()
        return completados == total_campos

    @property
    def estado_stepper(self):
        if self.campos_obligatorios_completados:
            return 'done'
        else:
            return 'default'

    class Meta:
        abstract = True


class Paso1RevisionFinalSubdere(PasoBase):
    competencia = models.OneToOneField(Competencia, on_delete=models.CASCADE, related_name='paso1_revision_final_subdere')
    regiones_seleccionadas = models.BooleanField(default=False)

    @property
    def nombre_paso(self):
        return 'Ámbito y recomendación de transferencia'

    @property
    def numero_paso(self):
        return 1

    def avance_numerico(self):
        total_campos = 2  # Dos campos obligatorios: 'ambito_definitivo_competencia' y 'regiones_seleccionadas'

        # Inicializa el contador de campos completados
        completados = 0

        # Verifica si 'ambito_definitivo_competencia' está completo
        if self.competencia.ambito_definitivo_competencia is not None:
            completados += 1

        # Verifica si 'regiones_seleccionadas' está marcado como True
        if self.regiones_seleccionadas:
            completados += 1

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"


class Paso2RevisionFinalSubdere(PasoBase):
    competencia = models.OneToOneField(Competencia, on_delete=models.CASCADE, related_name='paso2_revision_final_subdere')

    @property
    def nombre_paso(self):
        return 'Condiciones de transferencia'

    @property
    def numero_paso(self):
        return 2

    def avance_numerico(self):
        completados = 0
        total_campos = 4  # Inicia con 4 por los campos directos de Competencia

        # Comprobaciones para Recomendaciones Desfavorables
        recomendaciones = self.competencia.recomendaciones_desfavorables.all()
        for recomendacion in recomendaciones:
            if recomendacion.justificacion:
                completados += 1
            total_campos += 1

        # Comprobaciones para Temporalidad
        temporalidades = self.competencia.temporalidad_gradualidad.all()
        for temporalidad in temporalidades:
            # Se comprueba que haya regiones asociadas, que temporalidad no esté vacío, y que justificacion_temporalidad no esté vacío
            if temporalidad.region.count() > 0 and temporalidad.temporalidad and temporalidad.justificacion_temporalidad:
                # Si temporalidad es 'Temporal', entonces también se requiere que anios no sea None
                if temporalidad.temporalidad == 'Temporal' and temporalidad.anios is not None:
                    completados += 1
                # Si la temporalidad no es 'Temporal', se cuenta como completado sin necesidad de verificar el campo anios
                elif temporalidad.temporalidad == 'Definitiva':
                    completados += 1
            total_campos += 1

        # Comprobaciones para campos de Competencia
        campos_competencia = [
            self.competencia.recursos_requeridos,
            self.competencia.modalidad_ejercicio,
            self.competencia.implementacion_acompanamiento,
            self.competencia.condiciones_ejercicio
        ]
        completados += sum([1 for campo in campos_competencia if campo])

        return completados, total_campos

    def avance(self):
        completados, total_campos = self.avance_numerico()
        return f"{completados}/{total_campos}"


class ImagenesRevisionSubdere(BaseModel):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagenes_revision_subdere/', blank=True, null=True)


