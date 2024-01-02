from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa3
from applications.competencias.models import Competencia
from applications.etapas.functions import (
    get_ultimo_editor,
    get_fecha_ultima_modificacion,
    calcular_tiempo_registro,
    obtener_estado_accion_generico,
)

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
    oficio_inicio_gore = serializers.SerializerMethodField()

    class Meta:
        model = Etapa3
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuario_notificado',
            'minuta_sectorial',
            'observacion_minuta_sectorial',
            'oficio_inicio_gore',
            'oficio_origen',
        ]


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
            usuario_grupo='DIPRES',
            conteo_condicion=1,
            nombre_singular=nombre_singular,
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )

    def get_minuta_sectorial(self, obj):
        return obtener_estado_accion_generico(
            self,
            condicion=obj.minuta_etapa3_enviada,
            condicion_anterior=obj.usuario_notificado,
            usuario_grupo='DIPRES',
            conteo_condicion=1,
            nombre_singular='Subir minuta',
            accion_usuario_grupo='Subir minuta',
            accion_general='Minuta pendiente',
            accion_finalizada_usuario_grupo='Ver minuta',
            accion_finalizada_general='Ver minuta',
        )

    def get_observacion_minuta_sectorial(self, obj):
        return obtener_estado_accion_generico(
            self,
            condicion=obj.observacion_minuta_sectorial_enviada,
            condicion_anterior=obj.minuta_etapa3_enviada,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir observación',
            accion_usuario_grupo='Subir observación',
            accion_general='Observación pendiente',
            accion_finalizada_usuario_grupo='Ver observación',
            accion_finalizada_general='Ver observación',
        )

    def get_oficio_inicio_gore(self, obj):
        return obtener_estado_accion_generico(
            self,
            condicion=obj.competencia.etapa3.oficio_origen,
            condicion_anterior=obj.competencia.etapa2.aprobada,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir oficio y su fecha para habilitar formulario GORE',
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )
