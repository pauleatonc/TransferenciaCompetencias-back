from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa5

from applications.etapas.functions import (
    get_ultimo_editor,
    get_fecha_ultima_modificacion,
    obtener_estado_accion_generico,
)

User = get_user_model()


class Etapa5Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    usuario_notificado = serializers.SerializerMethodField()
    oficio_inicio_dipres = serializers.SerializerMethodField()
    minuta_gore = serializers.SerializerMethodField()
    observacion_minuta_gore = serializers.SerializerMethodField()
    tipo_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Etapa5
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'calcular_tiempo_transcurrido',
            'plazo_dias',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuario_notificado',
            'oficio_inicio_dipres',
            'minuta_gore',
            'observacion_minuta_gore',
            'oficio_origen',
            'tipo_usuario',

            # Campos DIPRES etapa 5
            'comentario_minuta_etapa5',
            'archivo_minuta_etapa5',
            'minuta_etapa5_enviada',

            # Campos Revisión SUBDERE etapa 5
            'comentario_minuta_gore',
            'archivo_observacion_minuta_gore',
            'observacion_minuta_gore_enviada'

        ]

    def get_tipo_usuario(self, obj):
        return {"DIPRES"}

    def get_ultimo_editor(self, obj):
        return get_ultimo_editor(self, obj)

    def get_fecha_ultima_modificacion(self, obj):
        return get_fecha_ultima_modificacion(self, obj)

    def get_usuario_notificado(self, obj):
        usuarios_dipres = obj.competencia.usuarios_dipres.all()
        usuarios_info = [f'{usuario.nombre_completo} ({usuario.email})' for usuario in usuarios_dipres]
        nombre_singular = f'Notificar a {", ".join(usuarios_info)}'

        return obtener_estado_accion_generico(
            self,
            condicion=obj.usuario_notificado,
            condicion_anterior=obj.competencia.etapa2.aprobada,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular=nombre_singular,
            accion_usuario_grupo='Agregar usuario',
            accion_general='Usuario pendiente',
            accion_finalizada_usuario_grupo='Finalizada',
            accion_finalizada_general='Finalizada',
        )

    def get_oficio_inicio_dipres(self, obj):
        return obtener_estado_accion_generico(
            self,
            id=obj.competencia.etapa5.id,
            condicion=obj.oficio_origen,
            condicion_anterior=obj.usuario_notificado,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir oficio y su fecha para habilitar minuta DIPRES',
            nombre_plural='',
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )

    def get_minuta_gore(self, obj):
        return obtener_estado_accion_generico(
            self,
            id=obj.competencia.etapa5.id,
            condicion=obj.minuta_etapa5_enviada,
            condicion_anterior=obj.oficio_origen,
            usuario_grupo='DIPRES',
            conteo_condicion=1,
            nombre_singular='Subir minuta',
            accion_usuario_grupo='Subir minuta',
            accion_general='Minuta pendiente',
            accion_finalizada_usuario_grupo='Ver minuta',
            accion_finalizada_general='Ver minuta',
        )
    def get_observacion_minuta_gore(self, obj):
        return obtener_estado_accion_generico(
            self,
            id=obj.competencia.etapa5.id,
            condicion=obj.observacion_minuta_gore_enviada,
            condicion_anterior=obj.minuta_etapa5_enviada,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Revisión SUBDERE',
            accion_usuario_grupo='Subir Observaciones',
            accion_general='Observaciones pendientes',
            accion_finalizada_usuario_grupo='Ver Observaciones',
            accion_finalizada_general='Ver Observaciones',
        )
