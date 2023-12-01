from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa2, ObservacionSectorial
from applications.formularios_sectoriales.models import FormularioSectorial

User = get_user_model()


class Etapa2Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    usuarios_notificados = serializers.SerializerMethodField()
    formulario_sectorial = serializers.SerializerMethodField()
    observaciones_sectorial = serializers.SerializerMethodField()

    class Meta:
        model = Etapa2
        fields = [
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'plazo_dias',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuarios_notificados',
            'formulario_sectorial',
            'observaciones_sectorial'
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
        user = self.context['request'].user
        es_usuario_subdere = user.groups.filter(name='SUBDERE').exists()
        sectores = obj.competencia.sectores.all()
        detalle = []

        for sector in sectores:
            usuario_sectorial = obj.competencia.usuarios_sectoriales.filter(sector=sector).first()

            if usuario_sectorial:
                detalle.append({
                    "nombre": f"Notificar a {usuario_sectorial.nombre_completo} ({usuario_sectorial.email}) - {sector.nombre}",
                    "estado": 'finalizada',
                    "accion": 'Finalizada'
                })
            else:
                accion = 'Asignar usuario' if es_usuario_subdere else 'Usuario pendiente'
                estado = 'revision' if es_usuario_subdere else 'pendiente'
                detalle.append({
                    "nombre": f"Asociar usuario Sectorial a {sector.nombre}",
                    "estado": estado,
                    "accion": accion
                })

        if len(sectores) <= 1:
            # Si solo hay un sector, devuelve directamente el detalle
            return detalle

        # Crear resumen para múltiples sectores
        resumen_estado = 'finalizada' if obj.usuarios_notificados else 'revision' if es_usuario_subdere else 'pendiente'
        resumen_accion = 'Finalizada' if obj.usuarios_notificados else 'Asignar usuarios' if es_usuario_subdere else 'Usuarios pendientes'
        resumen = {
            "nombre": 'Usuarios Sectoriales notificados' if obj.usuarios_notificados else 'Usuarios Sectoriales pendientes',
            "estado": resumen_estado,
            "accion": resumen_accion
        }

        detalle = self.reordenar_detalle(detalle, self.context['request'].user)

        return {
            "usuarios_notificados": [resumen],
            "detalle_usuarios_notificados": detalle
        }

    def get_formulario_sectorial(self, obj):
        user = self.context['request'].user
        es_usuario_sectorial = user.groups.filter(name='Usuario Sectorial').exists()
        sectores = obj.competencia.sectores.all()
        detalle = []

        for sector in sectores:
            formulario_sectorial = FormularioSectorial.objects.filter(competencia=obj.competencia,
                                                                      sector=sector).first()
            if formulario_sectorial:
                estado_revision = es_usuario_sectorial and obj.usuarios_notificados
                estado = 'finalizada' if formulario_sectorial.formulario_enviado else 'revision' if estado_revision else 'pendiente'
                accion = 'Ver Formulario' if formulario_sectorial.formulario_enviado else 'Subir Formulario' if es_usuario_sectorial else 'Formulario pendiente'
                detalle_formulario = {
                    "nombre": f"Completar formulario Sectorial - {sector.nombre}",
                    "estado": estado,
                    "accion": accion
                }
                if formulario_sectorial.formulario_enviado:
                    detalle_formulario["registro_tiempo"] = self.calcular_tiempo_registro(obj, formulario_sectorial.fecha_envio)
                detalle.append(detalle_formulario)

        if len(sectores) <= 1:
            return detalle

        resumen_estado = 'finalizada' if obj.formulario_completo else 'revision'
        resumen_accion = 'Ver formularios' if obj.formulario_completo else 'En Estudio'
        resumen = {
            "nombre": 'Ver formularios Sectoriales' if obj.formulario_completo else 'Completar formularios Sectoriales',
            "estado": resumen_estado,
            "accion": resumen_accion
        }

        detalle = self.reordenar_detalle(detalle, self.context['request'].user)

        return {
            "formularios_sectoriales": [resumen],
            "detalle_formularios_sectoriales": detalle
        }

    def get_observaciones_sectorial(self, obj):
        user = self.context['request'].user
        es_subdere = user.groups.filter(name='SUBDERE').exists()
        formularios_sectoriales = FormularioSectorial.objects.filter(competencia=obj.competencia)
        observaciones = ObservacionSectorial.objects.filter(formulario_sectorial__in=formularios_sectoriales)

        detalle = []
        for formulario in formularios_sectoriales:
            observacion = observaciones.filter(formulario_sectorial=formulario).first()
            if observacion:
                estado_revision = es_subdere and obj.formulario_completo
                estado = 'finalizada' if observacion.observacion_enviada else 'revision' if estado_revision else 'pendiente'
                accion = 'Ver Observación' if observacion.observacion_enviada else 'Subir Observación' if es_subdere else 'Observación pendiente'
                detalle.append({
                    "nombre": f"Observación del formulario sectorial ({formulario.sector.nombre})",
                    "estado": estado,
                    "accion": accion
                })

        # Si solo hay una observación, devuelve directamente el detalle
        if len(detalle) <= 1:
            return detalle

        # Verificar si todas las observaciones han sido enviadas
        todas_observaciones_enviadas = all(observacion.observacion_enviada for observacion in observaciones)
        estado_resumen = 'finalizada' if todas_observaciones_enviadas else 'revision'
        accion_resumen = 'Ver Observaciones' if todas_observaciones_enviadas else 'En Estudio'
        resumen = {
            "nombre": 'Observaciones de formularios sectoriales',
            "estado": estado_resumen,
            "accion": accion_resumen
        }

        detalle = self.reordenar_detalle(detalle, self.context['request'].user)

        return {
            "resumen_observaciones_sectoriales": [resumen],
            "detalle_observaciones_sectoriales": detalle
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

        nombre_sector_usuario = user.sector.nombre if user.sector else None

        for d in detalle:
            if user.nombre_completo in d['nombre'] or (nombre_sector_usuario and nombre_sector_usuario in d['nombre']):
                usuario_principal.append(d)
            else:
                otros.append(d)

        return usuario_principal + otros