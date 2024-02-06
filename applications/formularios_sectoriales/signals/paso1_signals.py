from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import MarcoJuridico, OrganigramaRegional, FormularioSectorial, Paso1
from applications.regioncomuna.models import Region


@receiver(post_save, sender=FormularioSectorial)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso1
        Paso1.objects.create(formulario_sectorial=instance)


@receiver(post_save, sender=FormularioSectorial)
def crear_relaciones_formulario(sender, instance, created, **kwargs):
    if created:
        # Crear una instancia de MarcoJuridico para el nuevo FormularioSectorial
        MarcoJuridico.objects.create(formulario_sectorial=instance)


@receiver(post_save, sender=FormularioSectorial)
def crear_organigramas_regionales_para_formulario(sender, instance, created, **kwargs):
    if created:
        competencia = instance.competencia
        for region in competencia.regiones.all():
            OrganigramaRegional.objects.create(
                formulario_sectorial=instance,
                region=region
            )

@receiver(m2m_changed, sender=Competencia.regiones.through)
def crear_o_eliminar_organigramas_regionales(sender, instance, action, pk_set, **kwargs):
    # Acción después de agregar regiones a una competencia
    if action == 'post_add':
        # Para cada FormularioSectorial asociado a la Competencia
        for formulario_sectorial in FormularioSectorial.objects.filter(competencia=instance):
            # Crear OrganigramaRegional para cada nueva región asociada a la competencia
            for region_pk in pk_set:
                region = Region.objects.get(pk=region_pk)
                OrganigramaRegional.objects.get_or_create(
                    formulario_sectorial=formulario_sectorial,
                    region=region
                )

    # Acción después de eliminar regiones de una competencia
    elif action == 'post_remove':
        # Para cada FormularioSectorial asociado a la Competencia
        for formulario_sectorial in FormularioSectorial.objects.filter(competencia=instance):
            # Eliminar OrganigramaRegional para cada región desasociada de la competencia
            for region_pk in pk_set:
                OrganigramaRegional.objects.filter(
                    formulario_sectorial=formulario_sectorial,
                    region_id=region_pk
                ).delete()




