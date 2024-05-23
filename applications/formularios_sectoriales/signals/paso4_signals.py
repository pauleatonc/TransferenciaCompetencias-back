from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from ..models import *


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso4
        Paso4Encabezado.objects.create(formulario_sectorial=instance)


@receiver(m2m_changed, sender=Competencia.regiones.through)
def crear_instancias_relacionadas(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for formulario_sectorial in FormularioSectorial.objects.filter(competencia=instance):
            for region_pk in pk_set:
                region = Region.objects.get(pk=region_pk)
                # Crear instancias de Paso4
                Paso4.objects.get_or_create(
                    formulario_sectorial=formulario_sectorial,
                    region=region
                )
                # Crear indicadores de desempeño
                IndicadorDesempeno.objects.get_or_create(
                    formulario_sectorial=formulario_sectorial,
                    region=region
                )
    elif action == 'post_remove':
        for formulario_sectorial in FormularioSectorial.objects.filter(competencia=instance):
            for region_pk in pk_set:
                Paso4.objects.filter(
                    formulario_sectorial=formulario_sectorial,
                    region_id=region_pk
                ).delete()
                IndicadorDesempeno.objects.filter(
                    formulario_sectorial=formulario_sectorial,
                    region_id=region_pk
                ).delete()