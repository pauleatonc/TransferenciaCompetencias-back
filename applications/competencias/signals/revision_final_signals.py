from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import (
    Competencia,
    RecomendacionesDesfavorables,
    Temporalidad,
    Gradualidad,
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


@receiver(m2m_changed, sender=Competencia.regiones.through)
def replicar_region_en_recomendadas(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        with transaction.atomic():
            # Agrega las nuevas regiones a regiones_recomendadas
            for pk in pk_set:
                instance.regiones_recomendadas.add(pk)


@receiver(m2m_changed, sender=Competencia.regiones_recomendadas.through)
def actualizar_recomendaciones_desfavorables(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        with transaction.atomic():
            # Actualiza 'regiones_seleccionadas' a False si existen cambios en 'regiones_recomendadas'
            if hasattr(instance, 'paso1_revision_final_subdere'):
                paso1 = instance.paso1_revision_final_subdere
                paso1.regiones_seleccionadas = False
                paso1.save()

            # Determina las regiones que están en 'regiones' pero no en 'regiones_recomendadas'
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
        # Si se agregan regiones a regiones_recomendadas, y es la primera vez, creamos Temporalidad y Gradualidad
        if instance.regiones_recomendadas.count() > 0 and not instance.temporalidad.exists() and not instance.gradualidad.exists():
            Temporalidad.objects.create(
                competencia=instance,
                # Aquí puedes establecer los campos adicionales como 'temporalidad' y 'justificacion_temporalidad'
            )
            Gradualidad.objects.create(
                competencia=instance,
                # Aquí puedes establecer los campos adicionales como 'gradualidad_meses' y 'justificacion_gradualidad'
            )

    elif action == "post_remove" or action == "post_clear":
        # Si se eliminan todas las regiones de regiones_recomendadas, eliminamos las instancias de Temporalidad y Gradualidad
        if instance.regiones_recomendadas.count() == 0:
            instance.temporalidad.all().delete()
            instance.gradualidad.all().delete()

