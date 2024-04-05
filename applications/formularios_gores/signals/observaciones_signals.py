from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.formularios_gores.models import ObservacionesSubdereFormularioGORE, FormularioGORE


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        ObservacionesSubdereFormularioGORE.objects.create(formulario_gore=instance)


@receiver(post_save, sender=ObservacionesSubdereFormularioGORE)
def verificar_observaciones_enviadas(sender, instance, **kwargs):
    # Comprobar si la observación actual fue enviada
    if instance.observacion_enviada:
        # Obtener todas las instancias de FormularioGORE asociadas a la misma Competencia que el formulario actual
        formularios_gore = FormularioGORE.objects.filter(competencia=instance.formulario_gore.competencia)

        # Verificar si todas las ObservacionesSubdereFormularioGORE asociadas a los formularios_gore están enviadas
        todas_enviadas = all([
            obs.observacion_enviada for obs in
            ObservacionesSubdereFormularioGORE.objects.filter(formulario_gore__in=formularios_gore)
        ])

        # Si todas las observaciones han sido enviadas, actualizar el estado de la Competencia
        if todas_enviadas:
            competencia = instance.formulario_gore.competencia
            competencia.estado = 'FIN'
            if not competencia.fecha_fin:
                competencia.fecha_fin = timezone.now()
            competencia.save(update_fields=['estado', 'fecha_fin'])