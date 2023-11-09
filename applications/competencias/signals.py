from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from django.conf import settings

@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
def crear_formularios_sectoriales(sender, instance, action, pk_set, **kwargs):
    # Asegúrate de que solo actuamos en la acción 'post_add' para agregar usuarios
    if action == 'post_add':
        etapa1 = instance.etapa1_set.first()  # Asumiendo que existe una relación inversa desde Competencia a Etapa1
        for user_pk in pk_set:
            usuario = settings.AUTH_USER_MODEL.objects.get(pk=user_pk)
            FormularioSectorial.objects.get_or_create(
                etapa=etapa1,
                usuario=usuario,
                defaults={'nombre': f'Formulario Sectorial de {usuario.username}'}
            )
