from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa2
from applications.formularios_sectoriales.models import FormularioSectorial, ObservacionesSubdereFormularioSectorial
from applications.etapas.functions import (
    get_ultimo_editor,
    get_fecha_ultima_modificacion,
    calcular_tiempo_registro,
    obtener_estado_accion_generico,
    reordenar_detalle,
)

User = get_user_model()


class Etapa2Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    usuarios_notificados = serializers.SerializerMethodField()
    oficio_inicio_sectorial = serializers.SerializerMethodField()
    formulario_sectorial = serializers.SerializerMethodField()
    observaciones_sectorial = serializers.SerializerMethodField()
    tipo_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Etapa2
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'plazo_dias',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuarios_notificados',
            'oficio_inicio_sectorial',
            'formulario_sectorial',
            'observaciones_sectorial',
            'oficio_origen',
            'tipo_usuario',
            'observaciones_completas'
        ]

    def get_tipo_usuario(self, obj):
        return {"Sectorial"}

    def get_ultimo_editor(self, obj):
        return get_ultimo_editor(self, obj)

    def get_fecha_ultima_modificacion(self, obj):
        return get_fecha_ultima_modificacion(self, obj)

    def reordenar_detalle(self, detalle, user):
        return reordenar_detalle(self, detalle, user)

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

    def get_oficio_inicio_sectorial(self, obj):
        return obtener_estado_accion_generico(
            self,
            id=obj.competencia.etapa2.id,
            condicion=obj.oficio_origen,
            condicion_anterior=obj.usuarios_notificados,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir oficio y su fecha para habilitar formulario sectorial',
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )

    def get_formulario_sectorial(self, obj):
        user = self.context['request'].user
        es_usuario_sectorial = obj.competencia.usuarios_sectoriales.filter(id=user.id).exists()
        sectores = obj.competencia.sectores.all()
        detalle = []

        for sector in sectores:
            formulario_sectorial = FormularioSectorial.objects.filter(competencia=obj.competencia,
                                                                      sector=sector).first()
            if formulario_sectorial:
                # Verifica si el usuario es sectorial y si el sector del formulario coincide con el del usuario
                usuario_sector_correcto = es_usuario_sectorial and user.sector == sector
                estado_revision = usuario_sector_correcto and obj.oficio_origen
                estado = 'finalizada' if formulario_sectorial.formulario_enviado else 'revision' if estado_revision else 'pendiente'
                accion = 'Ver Formulario' if formulario_sectorial.formulario_enviado else 'Subir Formulario' if usuario_sector_correcto else 'Formulario pendiente'

                # Obtener antecedente_adicional_sectorial y descripcion_antecedente
                antecedente_adicional_sectorial = formulario_sectorial.antecedente_adicional_sectorial.url if formulario_sectorial.antecedente_adicional_sectorial else 'No aplica'
                descripcion_antecedente = formulario_sectorial.descripcion_antecedente if formulario_sectorial.descripcion_antecedente else 'No aplica'

                detalle_formulario = {
                    "id": formulario_sectorial.id,
                    "sector_id": sector.id,
                    "nombre": f"Completar formulario Sectorial - {sector.nombre}",
                    "estado": estado,
                    "accion": accion,
                    "antecedente_adicional_sectorial": antecedente_adicional_sectorial,
                    "descripcion_antecedente": descripcion_antecedente
                }

                if formulario_sectorial.formulario_enviado:
                    detalle_formulario["registro_tiempo"] = calcular_tiempo_registro(self, obj.fecha_inicio,
                                                                                     formulario_sectorial.fecha_envio)

                detalle.append(detalle_formulario)

        if len(sectores) <= 1:
            return detalle

        resumen_estado = 'finalizada' if obj.formulario_completo else 'revision'
        resumen_accion = 'Ver formularios' if obj.formulario_completo else 'Formularios pendientes'
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
        es_usuario_sectorial = user.groups.filter(name='Usuario Sectorial').exists()
        formularios_sectoriales = FormularioSectorial.objects.filter(competencia=obj.competencia)
        observaciones = ObservacionesSubdereFormularioSectorial.objects.filter(
            formulario_sectorial__in=formularios_sectoriales)

        detalle = []
        for formulario in formularios_sectoriales:
            observacion = observaciones.filter(formulario_sectorial=formulario).first()
            if observacion:
                estado_revision = es_subdere and obj.formulario_completo
                estado = 'finalizada' if observacion.observacion_enviada else 'revision' if estado_revision else 'pendiente'

                if observacion.observacion_enviada and (es_subdere or es_usuario_sectorial):
                    accion = 'Ver Observación'
                elif observacion.observacion_enviada and not es_subdere and not es_usuario_sectorial:
                    accion = 'Finalizada'
                elif es_subdere:
                    accion = 'Subir Observación'
                else:
                    accion = 'Observación pendiente'

                detalle.append({
                    "id": formulario.id,
                    "nombre": f"Observación del formulario sectorial ({formulario.sector.nombre})",
                    "estado": estado,
                    "accion": accion
                })

        # Si solo hay una observación, devuelve directamente el detalle
        if len(detalle) <= 1:
            return detalle

        # Verificar si todas las observaciones han sido enviadas
        todas_observaciones_enviadas = all(observacion.observacion_enviada for observacion in observaciones)

        if todas_observaciones_enviadas:
            if es_subdere or es_usuario_sectorial:
                accion_resumen = 'Ver Observaciones'
            else:
                accion_resumen = 'Observaciones Finalizadas'
        else:
            accion_resumen = 'Observaciones pendientes'

        estado_resumen = 'finalizada' if todas_observaciones_enviadas else 'revision'
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



