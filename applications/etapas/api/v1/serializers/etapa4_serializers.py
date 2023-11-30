from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa4

User = get_user_model()


class Etapa4Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    usuarios_gore_notificados = serializers.SerializerMethodField()
    #formulario_gore_completo = serializers.SerializerMethodField()

    class Meta:
        model = Etapa4
        fields = [
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuarios_gore_notificados',
            #'formulario_gore_completo',
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

    def get_usuarios_gore_notificados(self, obj):
        user = self.context['request'].user
        es_usuario_subdere = user.groups.filter(name='SUBDERE').exists()
        regiones = obj.competencia.regiones.all()
        detalle = []

        for region in regiones:
            usuario_gore = obj.competencia.usuarios_gore.filter(region=region).first()
            if usuario_gore:
                detalle.append({
                    "nombre": f"Notificar a {usuario_gore.nombre_completo} ({usuario_gore.email}) - {region.region}",
                    "estado": 'finalizada',
                    "accion": 'Finalizada'
                })
            else:
                accion = 'Asignar usuario' if es_usuario_subdere else 'Usuario pendiente'
                estado = 'revision' if es_usuario_subdere else 'pendiente'
                detalle.append({
                    "nombre": f"Asociar usuario GORE a {region.region}",
                    "estado": estado,
                    "accion": accion
                })

        if len(regiones) <= 1:
            # Si solo hay una región, devuelve directamente el detalle
            return detalle

        # Crear resumen para múltiples regiones
        resumen_estado = 'finalizada' if obj.usuarios_gore_notificados else 'revision' if es_usuario_subdere else 'pendiente'
        resumen_accion = 'Finalizada' if obj.usuarios_gore_notificados else 'Asignar usuarios' if es_usuario_subdere else 'Usuarios pendientes'
        resumen = {
            "nombre": 'Usuarios GORE notificados' if obj.usuarios_gore_notificados else 'Usuarios GORE pendientes',
            "estado": resumen_estado,
            "accion": resumen_accion
        }

        return {
            "usuarios_gore_notificados": [resumen],
            "detalle_usuarios_gore_notificados": detalle
        }