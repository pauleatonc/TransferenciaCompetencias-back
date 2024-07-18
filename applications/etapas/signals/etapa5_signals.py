from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa5
from applications.formularios_gores.models import ObservacionesSubdereFormularioGORE


@receiver(m2m_changed, sender=Competencia.usuarios_dipres.through)
def actualizar_etapa5_al_modificar_usuarios_dipres(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if isinstance(instance, Competencia):
            etapa5 = Etapa5.objects.filter(competencia=instance).first()
            if etapa5:
                etapa5.usuario_notificado = instance.usuarios_dipres.exists()
                etapa5.save()


@receiver(post_save, sender=ObservacionesSubdereFormularioGORE)
def comprobar_y_finalizar_observaciones_etapa5(sender, instance, **kwargs):
    # Comprobar si todas las observaciones han sido enviadas
    todas_enviadas = all(
        observacion.observacion_enviada for observacion in
        ObservacionesSubdereFormularioGORE.objects.filter(
            formulario_gore__competencia=instance.formulario_gore.competencia)
    )

    # Obtener Etapa2 relacionada con la competencia
    etapa5 = Etapa5.objects.filter(competencia=instance.formulario_gore.competencia).first()

    if todas_enviadas and etapa5:
        etapa5.observacion_minuta_gore_enviada = True
        etapa5.save()
