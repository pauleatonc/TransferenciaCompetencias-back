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
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = Etapa1
        fields = ['nombre_etapa', 'estado', 'competencia_creada', 'usuarios_vinculados', 'fecha_inicio', 'tiempo_transcurrido_registrado', 'ultimo_editor', 'fecha_ultima_modificacion']

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