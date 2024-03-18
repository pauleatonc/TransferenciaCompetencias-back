from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from applications.competencias.models import Competencia, RecomendacionesDesfavorables


@receiver(m2m_changed, sender=Competencia.regiones.through)
@receiver(m2m_changed, sender=Competencia.regiones_recomendadas.through)
def actualizar_recomendaciones_desfavorables(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        # Si se agregan, remueven o limpian las relaciones, procedemos a actualizar

        # Recuperamos todas las regiones actuales y las recomendadas
        regiones_actuales = set(instance.regiones.all())
        regiones_recomendadas = set(instance.regiones_recomendadas.all())

        # Determinamos las regiones que no están recomendadas
        regiones_no_recomendadas = regiones_actuales - regiones_recomendadas

        # Actualizamos las RecomendacionesDesfavorables
        # Primero, añadimos las nuevas recomendaciones desfavorables si no existen
        for region in regiones_no_recomendadas:
            RecomendacionesDesfavorables.objects.get_or_create(competencia=instance, region=region)

        # Luego, eliminamos las recomendaciones desfavorables que ya no aplican
        RecomendacionesDesfavorables.objects.filter(competencia=instance).exclude(region__in=regiones_no_recomendadas).delete()
