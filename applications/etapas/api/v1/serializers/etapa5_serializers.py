from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa5

User = get_user_model()


class Etapa5Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    usuario_notificado = serializers.SerializerMethodField()
    minuta_sectorial = serializers.SerializerMethodField()
    observacion_minuta_sectorial = serializers.SerializerMethodField()

    class Meta:
        model = Etapa5
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuario_notificado',
            'minuta_sectorial',
            'observacion_minuta_sectorial'
        ]

    def get_fecha_ultima_modificacion(self, obj):
        try:
            ultimo_registro = obj.historical.latest('history_date')
            if ultimo_registro:
                fecha_local = timezone.localtime(ultimo_registro.history_date)
                return fecha_local.strftime('%d/%m/%Y - %H:%M')
            return None
        except obj.historical.model.DoesNotExist:
            return None

    def get_ultimo_editor(self, obj):
        return self.obtener_ultimo_editor_de_historial(obj)

    def get_usuario_notificado(self, obj):
        return self.obtener_estado_accion_generico(
            condicion=obj.usuario_notificado,
            usuario_grupo='DIPRES',
            nombre_accion='Notificar a DIPRES',
            nombre_pendiente='Asociar usuario DIPRES a la competencia'
        )

    def get_minuta_sectorial(self, obj):
        return self.obtener_estado_accion_generico(
            condicion=obj.minuta_etapa5_enviada,
            usuario_grupo='DIPRES',
            nombre_accion='Subir minuta',
            nombre_pendiente='Subir minuta',
            siempre_pendiente=True
        )

    def get_observacion_minuta_sectorial(self, obj):
        return self.obtener_estado_accion_generico(
            condicion=obj.observacion_minuta_gore_enviada,
            usuario_grupo='SUBDERE',
            nombre_accion='Revisión SUBDERE',
            nombre_pendiente='Subir Observaciones',
            siempre_pendiente=True
        )

    # Funciones de ayuda
    def obtener_ultimo_editor_de_historial(self, obj):
        historial = obj.historical.all().order_by('-history_date')
        for record in historial:
            if record.history_user:
                return {
                    'nombre_completo': record.history_user.nombre_completo,
                    'perfil': record.history_user.perfil
                }
        return None

    def obtener_estado_accion_generico(self, condicion, usuario_grupo, nombre_accion, nombre_pendiente,
                                       siempre_pendiente=False):
        user = self.context['request'].user
        es_grupo_usuario = user.groups.filter(name=usuario_grupo).exists()

        # Para usuarios DIPRES, verificar si están en la lista de usuarios_dipres de la Competencia
        if usuario_grupo == 'DIPRES':
            es_grupo_usuario = es_grupo_usuario and self.instance.competencia.usuarios_dipres.filter(
                id=user.id).exists()

        if condicion:
            return {
                "nombre": nombre_accion,
                "estado": 'finalizada',
                "accion": 'Finalizada'
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