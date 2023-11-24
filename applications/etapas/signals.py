from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.etapas.models import Etapa1, Etapa2, ObservacionSectorial, Etapa3
from applications.formularios_sectoriales.models import FormularioSectorial


@receiver(post_save, sender=Etapa1)
def actualizar_etapa2(sender, instance, **kwargs):
    if instance.estado == 'finalizada':
        # Obtener o crear la instancia de Etapa2 asociada
        etapa2, created = Etapa2.objects.get_or_create(competencia=instance.competencia)

        # Actualizar estado y tiempo restante
        etapa2.usuarios_notificados = True
        if not etapa2.fecha_inicio:
            etapa2.fecha_inicio = timezone.now()

        etapa2.plazo_dias = instance.competencia.plazo_formulario_sectorial

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


@receiver(post_save, sender=ObservacionSectorial)
def comprobar_y_finalizar_etapa2(sender, instance, **kwargs):
    # Comprobar si todas las observaciones han sido enviadas
    todas_enviadas = all(
        observacion.observacion_enviada for observacion in
        ObservacionSectorial.objects.filter(formulario_sectorial__competencia=instance.formulario_sectorial.competencia)
    )

    if todas_enviadas:
        # Obtener Etapa2 y Etapa3 relacionadas con la competencia
        etapa2 = Etapa2.objects.filter(competencia=instance.formulario_sectorial.competencia).first()
        etapa3 = Etapa3.objects.filter(competencia=instance.formulario_sectorial.competencia).first()

        # Actualizar Etapa2
        if etapa2:
            etapa2.enviada = False
            etapa2.aprobada = True
            etapa2.save()

        # Configurar y guardar Etapa3
        if etapa3:
            etapa3.fecha_inicio = timezone.now()
            etapa3.save()