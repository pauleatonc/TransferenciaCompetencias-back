from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.formularios_gores.models import FormularioGORE
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.regioncomuna.models import Region
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5, ObservacionSectorial

from django.contrib.auth import get_user_model


@receiver(m2m_changed, sender=Competencia.regiones.through)
@transaction.atomic
def agregar_formulario_regional_por_region(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        # Asegúrate de que la instancia de Competencia está completamente guardada
        competencia = Competencia.objects.get(pk=instance.pk)
        for region_pk in pk_set:
            region = Region.objects.get(pk=region_pk)
            # Aquí se crea el formulario asociado al GORE
            FormularioGORE.objects.get_or_create(
                competencia=competencia,
                region=region,
                defaults={'nombre': f'Formulario GORE de {region.region} - {competencia.nombre}'}
            )


@receiver(post_save, sender=Competencia)
def crear_etapas_para_competencia(sender, instance, created, **kwargs):
    if created:
        # Crear otras etapas
        Etapa1.objects.get_or_create(competencia=instance)
        Etapa2.objects.get_or_create(competencia=instance)
        Etapa3.objects.get_or_create(competencia=instance)
        Etapa4.objects.get_or_create(competencia=instance)
        Etapa5.objects.get_or_create(competencia=instance)


@receiver(post_save, sender=Etapa1)
def actualizar_estado_y_fecha_competencia(sender, instance, **kwargs):
    competencia = instance.competencia
    actualizar = False

    # Actualizar fecha_inicio si es necesario
    if instance.fecha_inicio and competencia.fecha_inicio != instance.fecha_inicio:
        competencia.fecha_inicio = instance.fecha_inicio
        actualizar = True

    # Guardar cambios en la competencia si ha habido algún cambio
    if actualizar:
        competencia.save()
