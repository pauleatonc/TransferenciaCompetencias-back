from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from applications.competencias.models import (
    Competencia,
    RecomendacionesDesfavorables,
    Temporalidad,
    Paso1RevisionFinalSubdere,
    Paso2RevisionFinalSubdere
)
from applications.printer.views import save_complete_document_pdf


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

            # Asegura que todas las RecomendacionesDesfavorables estén actualizadas
            for region in regiones_no_recomendadas:
                recomendacion, created = RecomendacionesDesfavorables.objects.get_or_create(
                    competencia=instance,
                    region=region,
                    defaults={'justificacion': ''}  # Establece justificación como vacía si es nueva
                )
                if not created:
                    recomendacion.justificacion = ''  # Limpia justificación si ya existía
                    recomendacion.save()

            # Elimina las RecomendacionesDesfavorables que ya no aplican
            RecomendacionesDesfavorables.objects.filter(competencia=instance).exclude(
                region__in=regiones_no_recomendadas).delete()

            # Verifica si todas las regiones son desfavorables
            if not regiones_recomendadas:
                # Establece campos de Competencia como nulos o vacíos según corresponda
                instance.recursos_requeridos = ''
                instance.modalidad_ejercicio = None  # Establece a null
                instance.implementacion_acompanamiento = ''
                instance.condiciones_ejercicio = ''
                instance.save()


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
    # Evitar recursión verificando un atributo personalizado
    if hasattr(instance, '_updating_status'):
        return

    # Marcar que estamos actualizando para prevenir re-entrada
    setattr(instance, '_updating_status', True)

    try:
        if instance.formulario_final_enviado:
            # Registrar fecha_envio_formulario_final si aún no está establecida
            if not instance.fecha_envio_formulario_final:
                instance.fecha_envio_formulario_final = timezone.now()
                instance.save(update_fields=['fecha_envio_formulario_final'])

            # Comparar conjuntos de regiones
            regiones = set(instance.regiones.all())
            regiones_recomendadas = set(instance.regiones_recomendadas.all())

            # Establecer recomendacion_transferencia según la lógica proporcionada
            if regiones == regiones_recomendadas:
                recomendacion = 'Favorable'
            elif regiones & regiones_recomendadas:
                recomendacion = 'Favorable Parcial'
            else:
                recomendacion = 'Desfavorable'

            # Solo actualizar si hay un cambio para evitar re-entrada
            if instance.recomendacion_transferencia != recomendacion:
                instance.recomendacion_transferencia = recomendacion
                instance.save(update_fields=['recomendacion_transferencia'])

            # Generar y guardar el PDF si el formulario final ha sido enviado
            if instance.formulario_final_enviado:
                save_complete_document_pdf(instance.id)

    finally:
        # Quitar marca para permitir futuras actualizaciones
        delattr(instance, '_updating_status')


@receiver(pre_save, sender=Competencia)
def check_status_change(sender, instance, **kwargs):
    if instance.pk:
        # Comprueba el estado anterior del campo 'imprimir_formulario_final'
        previous = sender.objects.get(pk=instance.pk)
        if previous.imprimir_formulario_final != instance.imprimir_formulario_final:
            # Guarda el nuevo estado en una variable del objeto para acceder después del guardado
            instance._imprimir_formulario_final_changed = True

@receiver(post_save, sender=Competencia)
def generate_pdf_on_status_change(sender, instance, created, **kwargs):
    # Comprueba si la instancia es recién creada o si el campo específico cambió
    if hasattr(instance, '_imprimir_formulario_final_changed') and instance.imprimir_formulario_final:
        save_complete_document_pdf(instance.id)


