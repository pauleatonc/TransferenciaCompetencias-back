from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa1

User = get_user_model()


class Etapa1Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    competencia_creada = serializers.SerializerMethodField()
    usuarios_vinculados = serializers.SerializerMethodField()
    oficio_inicio_sectorial = serializers.SerializerMethodField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = Etapa1
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'competencia_creada',
            'usuarios_vinculados',
            'oficio_inicio_sectorial',
            'tiempo_transcurrido_registrado',
            'ultimo_editor',
            'fecha_ultima_modificacion'
        ]

    def get_competencia_creada(self, obj):
        return [{
            "nombre": "Competencia creada",
            "estado": "finalizada",
            "accion": "Finalizada"
        }]

    def get_usuarios_vinculados(self, obj):
        user = self.context['request'].user
        nombre = "Usuario sectorial vinculado a la competencia creada"
        if obj.competencia.sectores.count() > 1:
            nombre = "Usuarios sectoriales vinculados a la competencia creada"

        # Utiliza el campo 'usuarios_vinculados' directamente para determinar el estado
        estado = 'finalizada' if obj.usuarios_vinculados else 'pendiente'
        accion = "Usuario(s) pendiente(s)"

        if obj.usuarios_vinculados:
            if user.groups.filter(name='SUBDERE').exists():
                accion = "Editar usuarios"
            else:
                accion = "Finalizada"
        else:
            if not user.groups.filter(name='SUBDERE').exists():
                accion = "Usuario(s) pendiente(s)"

        return [{
            "nombre": nombre,
            "estado": estado,
            "accion": accion
        }]


    def get_ultimo_editor(self, obj):
        historial = obj.historical.all().order_by('-history_date')
        for record in historial:
            if record.history_user:
                return {
                    'nombre_completo': record.history_user.nombre_completo,
                    'perfil': record.history_user.perfil
                    # Asegúrate de que el campo 'profile' exista en tu modelo de User
                }
        return None

    def get_fecha_ultima_modificacion(self, obj):
        try:
            ultimo_registro = obj.historical.latest('history_date')
            if ultimo_registro:
                fecha_local = timezone.localtime(ultimo_registro.history_date)
                return fecha_local.strftime('%d/%m/%Y - %H:%M')
            return None
        except obj.historical.model.DoesNotExist:
            return None

    def get_oficio_inicio_sectorial(self, obj):
        return self.obtener_estado_accion_generico(
            condicion=obj.oficio_origen,
            usuario_grupo='SUBDERE',
            nombre_accion='Subir oficio y su fecha para habilitar formulario sectorial',
            nombre_pendiente='Subir oficio'
        )


    def obtener_estado_accion_generico(self, condicion, usuario_grupo, nombre_accion, nombre_pendiente,
                                       siempre_pendiente=False):
        user = self.context['request'].user
        es_grupo_usuario = user.groups.filter(name=usuario_grupo).exists()

        # Para usuarios DIPRES, verificar si están en la lista de usuarios_dipres de la Competencia
        if usuario_grupo == 'SUBDERE':
            es_grupo_usuario = es_grupo_usuario and self.instance.competencia.usuarios_dipres.filter(
                id=user.id).exists()

        if condicion:
            return {
                "nombre": nombre_accion,
                "estado": 'finalizada',
                "accion": 'Ver Oficio'
            }

        if siempre_pendiente:
            return {
                "nombre": nombre_pendiente,
                "estado": 'pendiente',
                "accion": nombre_pendiente
            }

        estado = 'revision' if es_grupo_usuario else 'pendiente'
        accion = nombre_accion if es_grupo_usuario else nombre_pendiente

        return {
            "nombre": nombre_accion,
            "estado": estado,
            "accion": accion
        }