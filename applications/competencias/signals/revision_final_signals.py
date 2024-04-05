from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.competencias.models import (
    Competencia,
    RecomendacionesDesfavorables,
    Temporalidad,
    Paso1RevisionFinalSubdere,
    Paso2RevisionFinalSubdere
)


@receiver(post_save, sender=Competencia)
@transaction.atomic
def crear_pasos_revision_final_subdere(sender, instance, created, **kwargs):
    if created:
        # Cuando se crea una nueva instancia de Competencia, automáticamente se crean las instancias de los pasos de revisión final
        Paso1RevisionFinalSubdere.objects.get_or_create(competencia=instance)
        Paso2RevisionFinalSubdere.objects.get_or_create(competencia=instance)


@receiver(m2m_changed, sender=Competencia.regiones_recomendadas.through)
def actualizar_recomendaciones_desfavorables(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        with transaction.atomic():

            regiones_actuales = set(instance.regiones.all())
            regiones_recomendadas = set(instance.regiones_recomendadas.all())
            regiones_no_recomendadas = regiones_actuales - regiones_recomendadas

            # Actualiza las RecomendacionesDesfavorables
            for region in regiones_no_recomendadas:
                RecomendacionesDesfavorables.objects.get_or_create(competencia=instance, region=region)

            # Elimina las RecomendacionesDesfavorables que ya no aplican
            RecomendacionesDesfavorables.objects.filter(competencia=instance).exclude(
                region__in=regiones_no_recomendadas).delete()


@receiver(m2m_changed, sender=Competencia.regiones_recomendadas.through)
def manejar_cambios_en_regiones_recomendadas(sender, instance, action, **kwargs):
    if action == "post_add":
        # Verificar si existen instancias de Temporalidad, si no, crear una
        if not instance.temporalidad_gradualidad.exists():
            temporalidad_instance = Temporalidad.objects.create(
                competencia=instance,
            )
            # Si solo hay una región en regiones_recomendadas, asignarla a la instancia de Temporalidad
            if instance.regiones_recomendadas.count() == 1:
                region_unica = instance.regiones_recomendadas.first()
                temporalidad_instance.region.add(region_unica)
                temporalidad_instance.save()

    elif action == "post_remove" or action == "post_clear":
        # Si se eliminan todas las regiones de regiones_recomendadas, eliminar las instancias de Temporalidad
        if instance.regiones_recomendadas.count() == 0:
            instance.temporalidad_gradualidad.all().delete()


@receiver(post_save, sender=Competencia)
def update_competencia_status(sender, instance, **kwargs):
    # Solo proceder si formulario_final_enviado ha sido marcado como True
    if instance.formulario_final_enviado:
        # Registrar fecha_fin si aún no está establecida
        if not instance.fecha_envio_formulario_final:
            instance.fecha_envio_formulario_final = timezone.now()
            instance.save(update_fields=['fecha_envio_formulario_final'])

        # Comparar conjuntos de regiones
        regiones = set(instance.regiones.all())
        regiones_recomendadas = set(instance.regiones_recomendadas.all())

        # Si ambas listas son idénticas, establecer como Favorable
        if regiones == regiones_recomendadas:
            instance.recomendacion_transferencia = 'Favorable'
        # Si hay intersección pero no son idénticas, establecer como Favorable Parcial
        elif regiones & regiones_recomendadas:
            instance.recomendacion_transferencia = 'Favorable Parcial'
        # Si no hay ninguna intersección, establecer como Desfavorable
        else:
            instance.recomendacion_transferencia = 'Desfavorable'

        instance.save(update_fields=['recomendacion_transferencia'])