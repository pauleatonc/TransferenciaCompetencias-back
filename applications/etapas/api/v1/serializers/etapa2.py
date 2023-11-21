from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.etapas.models import Etapa2
from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

User = get_user_model()

class Etapa2Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    tiempo_restante = serializers.ReadOnlyField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    usuarios_notificados = serializers.SerializerMethodField()
    formulario_sectorial = serializers.SerializerMethodField()

    class Meta:
        model = Etapa2
        fields = [
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'tiempo_restante',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuarios_notificados',
            'formulario_sectorial'
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

    def get_usuarios_notificados(self, obj):
        if obj.usuarios_notificados:
            usuarios_sectoriales = obj.competencia.usuarios_sectoriales.all()
            return [
                {
                    "nombre": f"Notificar a {usuario.nombre_completo} ({usuario.email}) - {usuario.sector.nombre}",
                    "estado": 'finalizada',
                    "accion": 'Finalizada'
                } for usuario in usuarios_sectoriales
            ]
        else:
            return [{
                "nombre": 'Notificar a usuarios Sectoriales',
                "estado": 'pendiente',
                "accion": 'Usuario(s) Pendiente(s)'
            }]

    def get_formulario_sectorial(self, obj):
        user = self.context['request'].user
        formularios_sectoriales = obj.competencia.formulariosectorial_set.all()
        sector_usuario = user.sector if user.groups.filter(name='Usuario Sectorial').exists() else None

        return [
            {
                "nombre": f"Completar formulario sectorial ({formulario.sector.nombre})",
                "estado": self.determinar_estado_formulario(formulario, sector_usuario),
                "accion": self.determinar_accion_formulario(formulario, sector_usuario)
            } for formulario in formularios_sectoriales
        ]

    def determinar_estado_formulario(self, formulario, sector_usuario):
        if formulario.formulario_enviado:
            return 'finalizada'
        return 'revision' if formulario.sector == sector_usuario else 'pendiente'

    def determinar_accion_formulario(self, formulario, sector_usuario):
        if formulario.sector == sector_usuario and not formulario.formulario_enviado:
            return 'Completar Formulario'
        return 'Ver Formulario'
