from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from applications.etapas.models import Etapa1

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

    def get_usuarios_vinculados(self, obj):
        return self.obtener_estado_accion_generico(
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
        return self.obtener_estado_accion_generico(
            condicion=obj.oficio_origen,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir oficio y su fecha para habilitar formulario sectorial',
            nombre_plural='',
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )

    def obtener_estado_accion_generico(self, condicion, usuario_grupo, conteo_condicion, nombre_singular,
                                       nombre_plural, accion_usuario_grupo, accion_general,
                                       accion_finalizada_usuario_grupo, accion_finalizada_general,
                                       siempre_pendiente=False):
        user = self.context['request'].user
        grupos_usuario = [grupo.strip() for grupo in usuario_grupo.split(',')]

        # Verificar si el usuario pertenece a al menos uno de los grupos especificados
        es_grupo_usuario = any(user.groups.filter(name=grupo).exists() for grupo in grupos_usuario)

        if es_grupo_usuario:
            return {
                "nombre": nombre_plural if conteo_condicion > 1 else nombre_singular,
                "estado": 'finalizada' if condicion else ('pendiente' if siempre_pendiente else 'revision'),
                "accion": accion_finalizada_usuario_grupo if condicion else accion_usuario_grupo
            }
        else:
            return {
                "nombre": nombre_plural if conteo_condicion > 1 else nombre_singular,
                "estado": 'finalizada' if condicion else 'pendiente',
                "accion": accion_finalizada_general if condicion else accion_general
            }


