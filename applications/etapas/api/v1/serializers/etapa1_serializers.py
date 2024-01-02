from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa1
from applications.etapas.functions import get_ultimo_editor, get_fecha_ultima_modificacion, obtener_estado_accion_generico


User = get_user_model()


class Etapa1Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    competencia_creada = serializers.SerializerMethodField()
    usuarios_vinculados = serializers.SerializerMethodField()
    oficio_inicio_sectorial = serializers.SerializerMethodField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = Etapa1
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'competencia_creada',
            'usuarios_vinculados',
            'oficio_inicio_sectorial',
            'tiempo_transcurrido_registrado',
            'ultimo_editor',
            'fecha_ultima_modificacion'
        ]

    def get_competencia_creada(self, obj):
        return [{
            "nombre": "Competencia creada",
            "estado": "finalizada",
            "accion": "Finalizada"
        }]

    def get_ultimo_editor(self, obj):
        return get_ultimo_editor(self, obj)

    def get_fecha_ultima_modificacion(self, obj):
        return get_fecha_ultima_modificacion(self, obj)

    def get_usuarios_vinculados(self, obj):
        return obtener_estado_accion_generico(
            self,
            condicion=obj.usuarios_vinculados,
            conteo_condicion=obj.competencia.usuarios_subdere.count(),
            usuario_grupo='SUBDERE',
            nombre_singular='Usuario sectorial vinculado a la competencia creada',
            nombre_plural='Usuarios sectoriales vinculados a la competencia creada',
            accion_usuario_grupo='Editar usuario(s)',
            accion_general ='Usuario(s) pendiente(s)',
            accion_finalizada_usuario_grupo='Editar usuario(s)',
            accion_finalizada_general='Finalizada'
        )

    def get_oficio_inicio_sectorial(self, obj):
        return obtener_estado_accion_generico(
            self,
            condicion=obj.competencia.etapa2.oficio_origen,
            condicion_anterior=obj.usuarios_vinculados,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir oficio y su fecha para habilitar formulario sectorial',
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )
