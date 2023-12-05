from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa4
from applications.formularios_gores.models import FormularioGORE

User = get_user_model()


class Etapa4Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    usuarios_gore = serializers.SerializerMethodField()
    formularios_gore = serializers.SerializerMethodField()

    class Meta:
        model = Etapa4
        fields = [
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuarios_gore',
            'formularios_gore',
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

    def get_usuarios_gore(self, obj):
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

        detalle = self.reordenar_detalle(detalle, self.context['request'].user)

        return {
            "usuarios_gore_notificados": [resumen],
            "detalle_usuarios_gore_notificados": detalle
        }

    def get_formularios_gore(self, obj):
        user = self.context['request'].user
        es_usuario_gore = obj.competencia.usuarios_gore.filter(id=user.id).exists()
        regiones = obj.competencia.regiones.all()
        detalle = []

        for region in regiones:
            formulario_gore = FormularioGORE.objects.filter(competencia=obj.competencia, region=region).first()
            if formulario_gore:
                estado_revision = es_usuario_gore and obj.usuarios_gore_notificados
                estado = 'finalizada' if formulario_gore.formulario_enviado else 'revision' if estado_revision else 'pendiente'
                accion = 'Ver Formulario' if formulario_gore.formulario_enviado else 'Subir Formulario' if es_usuario_gore else 'Formulario pendiente'
                detalle_formulario = {
                    "nombre": f"Completar formulario GORE - {region.region}",
                    "estado": estado,
                    "accion": accion
                }
                if formulario_gore.formulario_enviado:
                    detalle_formulario["registro_tiempo"] = self.calcular_tiempo_registro(obj,
                                                                                          formulario_gore.fecha_envio)
                detalle.append(detalle_formulario)

        if len(regiones) <= 1:
            return detalle

        resumen_estado = 'finalizada' if obj.formulario_gore_completo else 'revision'
        resumen_accion = 'Ver formularios' if obj.formulario_gore_completo else 'En Estudio'
        resumen = {
            "nombre": 'Ver formularios GORE' if obj.formulario_gore_completo else 'Completar formularios GORE',
            "estado": resumen_estado,
            "accion": resumen_accion
        }

        detalle = self.reordenar_detalle(detalle, self.context['request'].user)

        return {
            "formularios_gore_completos": [resumen],
            "detalle_formularios_gore": detalle
        }

    def calcular_tiempo_registro(self, etapa_obj, fecha_envio):
        if etapa_obj.fecha_inicio and fecha_envio:
            delta = fecha_envio - etapa_obj.fecha_inicio
            total_seconds = int(delta.total_seconds())
            dias = total_seconds // (24 * 3600)
            horas = (total_seconds % (24 * 3600)) // 3600
            minutos = (total_seconds % 3600) // 60
            return {'dias': dias, 'horas': horas, 'minutos': minutos}
        return {'dias': 0, 'horas': 0, 'minutos': 0}

    def reordenar_detalle(self, detalle, user):
        # Identificar si el usuario actual está mencionado en cada elemento de detalle
        usuario_principal = []
        otros = []

        nombre_region_usuario = user.region.region if user.region else None

        for d in detalle:
            if user.nombre_completo in d['nombre'] or (nombre_region_usuario and nombre_region_usuario in d['nombre']):
                usuario_principal.append(d)
            else:
                otros.append(d)

        return usuario_principal + otros