from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from django.utils import timezone

from applications.etapas.models import Etapa3, Etapa4
from applications.formularios_gores.models import FormularioGORE
from applications.regioncomuna.models import Region


@receiver(m2m_changed, sender=Competencia.usuarios_gore.through)
def actualizar_etapa4_al_modificar_usuarios_gore(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        etapa4 = instance.etapa4_set.first()

        if etapa4:
            todos_los_usuarios_asignados = True
            for region in instance.regiones.all():
                if not instance.usuarios_gore.filter(region=region).exists():
                    todos_los_usuarios_asignados = False
                    break

            etapa4.usuarios_gore_notificados = todos_los_usuarios_asignados

            etapa4.save()


@receiver(m2m_changed, sender=Competencia.regiones.through)
@transaction.atomic
def agregar_formulario_gore_por_region(sender, instance, action, pk_set, **kwargs):
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
