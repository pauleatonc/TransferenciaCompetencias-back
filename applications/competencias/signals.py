from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from django.contrib.auth import get_user_model


@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
def crear_formularios_sectoriales(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        User = get_user_model()  # Obtén el modelo de usuario
        etapa1 = instance.etapa1_set.first()  # Asumiendo que hay una relación directa
        for user_pk in pk_set:
            usuario = User.objects.get(pk=user_pk)  # Usa User en lugar de settings.AUTH_USER_MODEL
            FormularioSectorial.objects.get_or_create(
                etapa=etapa1,
                usuario=usuario,
                defaults={'nombre': f'Formulario Sectorial de {usuario.nombre_completo}'}
            )
