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
            formulario_sectorial = FormularioSectorial.objects.filter(competencia=obj.competencia, sector=sector).first()
            if formulario_sectorial and formulario_sectorial.formulario_enviado:
                detalle.append({
                    "nombre": f"Completar formulario sectorial - {sector.nombre}",
                    "estado": 'finalizada',
                    "accion": 'Ver formulario'
                })
            elif obj.usuarios_notificados:
                estado = 'revision' if es_usuario_sectorial and formulario_sectorial and formulario_sectorial.sector == user.sector else 'pendiente'
                accion = 'Subir Formulario' if estado == 'revision' else 'Formulario pendiente'
                detalle.append({
                    "nombre": f"Completar formulario sectorial - {sector.nombre}",
                    "estado": estado,
                    "accion": accion
                })
            else:
                estado = 'pendiente'
                accion = 'Formulario pendiente'
                detalle.append({
                    "nombre": f"Completar formulario sectorial - {sector.nombre}",
                    "estado": estado,
                    "accion": accion
                })

        if len(sectores) <= 1:
            return detalle

        resumen_estado = 'finalizada' if obj.formulario_completo else 'revision'
        resumen_accion = 'Ver formularios' if obj.formulario_completo else 'En Estudio'
        resumen = {
            "nombre": 'Ver formularios sectoriales' if obj.formulario_completo else 'Completar formularios sectoriales',
            "estado": resumen_estado,
            "accion": resumen_accion
        }

        return {
            "formularios_sectoriales_completos": [resumen],
            "detalle_formularios_sectoriales": detalle
        }

    def get_observaciones_sectorial(self, obj):
        user = self.context['request'].user
        es_subdere = user.groups.filter(name='SUBDERE').exists()
        es_usuario_sectorial = user.groups.filter(name='Usuario Sectorial').exists()

        # Obtener todos los formularios sectoriales para la competencia
        formularios_sectoriales = obj.competencia.formulariosectorial_set.all()
        # Obtener todas las observaciones para los formularios sectoriales
        observaciones = ObservacionSectorial.objects.filter(formulario_sectorial__in=formularios_sectoriales)
        # Priorizar la observación del sector del usuario autenticado si es un usuario sectorial
        if es_usuario_sectorial:
            observaciones = list(observaciones)
            observaciones_usuario_sectorial = [obs for obs in observaciones if
                                               obs.formulario_sectorial.sector == user.sector]
            observaciones = observaciones_usuario_sectorial + [obs for obs in observaciones if
                                                               obs not in observaciones_usuario_sectorial]
        # Verificar si todos los formularios están completos
        formulario_completo = Etapa2.objects.get(competencia=obj.competencia).formulario_completo
        # Verificar si todas las observaciones han sido enviadas
        todas_observaciones_enviadas = all(obs.observacion_enviada for obs in observaciones)

        # Determinar estado y acción del resumen
        estado_resumen = self.determinar_estado_resumen(formulario_completo, todas_observaciones_enviadas)
        accion_resumen = self.determinar_accion_resumen(es_subdere, todas_observaciones_enviadas)

        resumen = {
            "nombre": 'Observaciones de formularios sectoriales',
            "estado": estado_resumen,
            "accion": accion_resumen
        }

        detalle = [
            self.detalle_observacion(observacion, es_subdere, obj) for observacion in observaciones
        ]

        return {
            "resumen_observaciones_sectoriales": [resumen],
            "detalle_observaciones_sectoriales": detalle
        }

    def determinar_estado_resumen(self, formulario_completo, todas_observaciones_enviadas):
        if todas_observaciones_enviadas:
            return 'finalizada'
        return 'revision' if formulario_completo else 'pendiente'

    def determinar_accion_resumen(self, es_subdere, todas_observaciones_enviadas):
        if todas_observaciones_enviadas or not es_subdere:
            return 'Ver Observaciones'
        return 'Subir Observaciones'

    def detalle_observacion(self, observacion, es_subdere, obj):
        # Ajusta según los campos y la lógica de tu modelo ObservacionFormulario
        return {
            "nombre": f"Observación del formulario sectorial ({observacion.formulario_sectorial.sector.nombre})",
            "estado": self.determinar_estado_observacion(observacion, es_subdere),
            "accion": 'Subir Observación' if es_subdere else 'Ver Observación',
        }
        if observacion.observacion_enviada:
            detalle["registro_tiempo"] = self.calcular_tiempo_registro(etapa_obj, observacion.fecha_envio)
        return detalle

    def determinar_estado_observacion(self, observacion, es_subdere):
        if observacion.observacion_enviada:
            return 'finalizada'
        return 'revision' if es_subdere else 'pendiente'

    def calcular_tiempo_registro(self, etapa_obj, fecha_envio):
        if etapa_obj.fecha_inicio and fecha_envio:
            delta = fecha_envio - etapa_obj.fecha_inicio
            total_seconds = int(delta.total_seconds())
            dias = total_seconds // (24 * 3600)
            horas = (total_seconds % (24 * 3600)) // 3600
            minutos = (total_seconds % 3600) // 60
            return {'dias': dias, 'horas': horas, 'minutos': minutos}
        return {'dias': 0, 'horas': 0, 'minutos': 0}