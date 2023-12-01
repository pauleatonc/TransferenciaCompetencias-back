from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa3

User = get_user_model()


class Etapa3Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    usuario_notificado = serializers.SerializerMethodField()
    minuta_sectorial = serializers.SerializerMethodField()
    observacion_minuta_sectorial = serializers.SerializerMethodField()

    class Meta:
        model = Etapa3
        fields = [
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

    def get_usuario_notificado(self, obj):
        user = self.context['request'].user
        nombre = "Asociar usuario DIPRES a la competencia"
        es_usuario_subdere = user.groups.filter(name='SUBDERE').exists()

        if obj.usuario_notificado:
            usuario_dipres = obj.competencia.usuarios_gore.first()
            return {
                "nombre": f"Notificar a {usuario_dipres.nombre_completo} ({usuario_dipres.email})",
                "estado": 'finalizada',
                "accion": 'Finalizada'
            }

        estado = 'revision' if es_usuario_subdere else 'pendiente'
        accion = 'Agregar usuario' if es_usuario_subdere else 'Usuario pendiente'

        return {
            "nombre": nombre,
            "estado": estado,
            "accion": accion
        }

    def get_minuta_sectorial(self, obj):
        user = self.context['request'].user
        nombre = "Subir minuta"

        if obj.minuta_etapa3_enviada:
            return {
                "nombre": nombre,
                "estado": 'finalizada',
                "accion": 'Ver minuta'
            }

        if not obj.usuario_notificado:
            return {
                "nombre": nombre,
                "estado": 'pendiente',
                "accion": 'Subir minuta'
            }

        if obj.usuario_notificado and user.groups.filter(name='DIPRES').exists():
            return {
                "nombre": nombre,
                "estado": 'revision',
                "accion": 'Subir minuta'
            }

        return None

    def get_observacion_minuta_sectorial(self, obj):
        user = self.context['request'].user
        nombre = "Revisión SUBDERE"

        if obj.observacion_minuta_sectorial_enviada:
            return {
                "nombre": nombre,
                "estado": 'finalizada',
                "accion": 'Ver Observaciones'
            }

        if not obj.observacion_minuta_sectorial_enviada:
            return {
                "nombre": nombre,
                "estado": 'pendiente',
                "accion": 'Subir Observaciones'
            }

        if obj.usuario_notificado and obj.minuta_etapa3_enviada and user.groups.filter(name='SUBDERE').exists():
            return {
                "nombre": nombre,
                "estado": 'revision',
                "accion": 'Subir Observaciones'
            }

        return None