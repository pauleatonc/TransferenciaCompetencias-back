from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.etapas.models import Etapa2, ObservacionSectorial
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
    observaciones_sectorial = serializers.SerializerMethodField()

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
        numero_sectores = obj.competencia.sectores.count()
        usuarios_sectoriales = obj.competencia.usuarios_sectoriales.all()

        if numero_sectores <= 1:
            # Si solo hay un sector, muestra los usuarios individualmente
            return [
                {
                    "nombre": f"Notificar a {usuario.nombre_completo} ({usuario.email})",
                    "estado": 'finalizada' if obj.usuarios_notificados else 'revision',
                    "accion": 'Finalizada' if obj.usuarios_notificados else 'Asignar usuario'
                } for usuario in usuarios_sectoriales
            ]
        else:
            # Si hay más de un sector, muestra un resumen y detalles
            resumen = {
                "nombre": 'Usuarios notificados' if obj.usuarios_notificados else 'Usuarios pendientes',
                "estado": 'finalizada' if obj.usuarios_notificados else 'revision',
                "accion": 'Finalizada' if obj.usuarios_notificados else 'En Estudio'
            }

            detalle = [
                {
                    "nombre": f"Notificar a {usuario.nombre_completo} ({usuario.email}) - {usuario.sector.nombre}",
                    "estado": 'finalizada' if obj.usuarios_notificados else 'revision',
                    "accion": 'Finalizada' if obj.usuarios_notificados else 'Asignar usuario'
                } for usuario in usuarios_sectoriales
            ]

            return {
                "usuarios_notificados": [resumen],
                "detalle_usuarios_notificados": detalle
            }

    def get_formulario_sectorial(self, obj):
        user = self.context['request'].user
        formularios_sectoriales = obj.competencia.formulariosectorial_set.all()
        sector_usuario = user.sector if user.groups.filter(name='Usuario Sectorial').exists() else None
        numero_formularios = formularios_sectoriales.count()

        # Cuenta el número de formularios no enviados
        formularios_no_enviados = sum(not f.formulario_enviado for f in formularios_sectoriales)

        if numero_formularios <= 1:
            # Si solo hay un formulario, muestra el detalle
            return [
                {
                    "nombre": f"Completar formulario sectorial ({formulario.sector.nombre})",
                    "estado": self.determinar_estado_formulario(formulario, sector_usuario),
                    "accion": self.determinar_accion_formulario(formulario, sector_usuario)
                } for formulario in formularios_sectoriales
            ]
        else:
            # Determina el texto para la acción según la cantidad de formularios no enviados
            texto_accion = 'Formulario Incompleto' if formularios_no_enviados == 1 else 'Formularios Incompletos'

            resumen = {
                "nombre": 'Formularios sectoriales',
                "estado": 'revision' if formularios_no_enviados > 0 else 'finalizada',
                "accion": texto_accion if formularios_no_enviados > 0 else 'Ver Formularios'
            }

            detalle = [
                {
                    "nombre": f"Completar formulario sectorial ({formulario.sector.nombre})",
                    "estado": self.determinar_estado_formulario(formulario, sector_usuario),
                    "accion": self.determinar_accion_formulario(formulario, sector_usuario)
                } for formulario in formularios_sectoriales
            ]

            return {
                "resumen_formularios_sectoriales": [resumen],
                "detalle_formularios_sectoriales": detalle
            }

    def determinar_estado_formulario(self, formulario, sector_usuario):
        if formulario.formulario_enviado:
            return 'finalizada'
        return 'revision' if formulario.sector == sector_usuario else 'pendiente'

    def determinar_accion_formulario(self, formulario, sector_usuario):
        if formulario.formulario_enviado:
            return 'Ver Formulario'
        return 'Completar Formulario'

    def get_observaciones_sectorial(self, obj):
        user = self.context['request'].user
        es_subdere = user.groups.filter(name='SUBDERE').exists()

        # Obtener todos los formularios sectoriales para la competencia
        formularios_sectoriales = obj.competencia.formulariosectorial_set.all()
        # Obtener todas las observaciones para los formularios sectoriales
        observaciones = ObservacionSectorial.objects.filter(formulario_sectorial__in=formularios_sectoriales)
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
            self.detalle_observacion(observacion, es_subdere) for observacion in observaciones
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

    def detalle_observacion(self, observacion, es_subdere):
        # Ajusta según los campos y la lógica de tu modelo ObservacionFormulario
        return {
            "nombre": f"Observación del formulario sectorial ({observacion.formulario_sectorial.sector.nombre})",
            "estado": self.determinar_estado_observacion(observacion, es_subdere),
            "accion": 'Subir Observación' if es_subdere else 'Ver Observación'
        }

    def determinar_estado_observacion(self, observacion, es_subdere):
        if observacion.observacion_enviada:
            return 'finalizada'
        return 'revision' if es_subdere else 'pendiente'