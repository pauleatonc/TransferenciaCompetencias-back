from django.db import transaction
from django.utils import timezone

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1, Etapa2
from applications.formularios_sectoriales.models import FormularioSectorial, Paso1, OrganigramaRegional
from applications.regioncomuna.models import Region
from applications.formularios_sectoriales.models import ObservacionesSubdereFormularioSectorial
from applications.sectores_gubernamentales.models import SectorGubernamental


@receiver(m2m_changed, sender=Competencia.regiones.through)
@transaction.atomic
def crear_organigramas_regionales(sender, instance, action, pk_set, **kwargs):
    if instance.pk and action == 'post_add':
        for sector in instance.sectores.all():
            formulario_sectorial, created = FormularioSectorial.objects.get_or_create(
                competencia=instance,
                sector=sector,
                defaults={'nombre': f'Formulario Sectorial de {sector.nombre} - {instance.nombre}'}
            )

            if created:
                # Crear OrganigramaRegional para cada región asociada a la competencia
                for region_pk in pk_set:
                    region = Region.objects.get(pk=region_pk)
                    OrganigramaRegional.objects.create(formulario_sectorial=formulario_sectorial, region=region)


@receiver(post_save, sender=Etapa1)
def actualizar_etapa2_con_estado_etapa1(sender, instance, **kwargs):
    # Obtener o crear la instancia de Etapa2 asociada
    etapa2, created = Etapa2.objects.get_or_create(competencia=instance.competencia)

    if instance.estado == 'finalizada':
        # Si Etapa1 se ha finalizado, actualiza Etapa2
        etapa2.usuarios_notificados = True
        etapa2.plazo_dias = instance.competencia.plazo_formulario_sectorial
    else:
        # Si Etapa1 no está finalizada, asegúrate de que usuarios_notificados en Etapa2 sea False
        etapa2.usuarios_notificados = False

    etapa2.save()


@receiver(post_save, sender=FormularioSectorial)
def actualizar_estado_formulario_completo_sectorial(sender, instance, **kwargs):
    # Comprobar si todos los formularios sectoriales están enviados
    todos_enviados = all(
        formulario.formulario_enviado for formulario in
        FormularioSectorial.objects.filter(competencia=instance.competencia)
    )

    # Obtener la instancia de Etapa2 asociada a la competencia
    etapa2 = Etapa2.objects.filter(competencia=instance.competencia).first()

    if etapa2:
        # Actualizar formulario_completo en función del estado de los formularios
        etapa2.formulario_completo = todos_enviados

        # Si todos los formularios están enviados, cambiar el estado de Etapa2 a 'en_revision'
        if todos_enviados:
            etapa2.enviada = True

        etapa2.save()


@receiver(post_save, sender=ObservacionesSubdereFormularioSectorial)
def comprobar_y_finalizar_etapa2(sender, instance, **kwargs):
    # Comprobar si todas las observaciones han sido enviadas
    todas_enviadas = all(
        observacion.observacion_enviada for observacion in
        ObservacionesSubdereFormularioSectorial.objects.filter(formulario_sectorial__competencia=instance.formulario_sectorial.competencia)
    )

    if todas_enviadas:
        # Obtener Etapa2 y Etapa3 relacionadas con la competencia
        etapa2 = Etapa2.objects.filter(competencia=instance.formulario_sectorial.competencia).first()

        # Actualizar Etapa2
        if etapa2:
            etapa2.enviada = False
            etapa2.aprobada = True
            etapa2.save()