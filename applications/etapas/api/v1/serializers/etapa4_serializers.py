from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.etapas.models import Etapa4
from applications.formularios_gores.models import FormularioGORE

from applications.etapas.functions import (
    get_ultimo_editor,
    get_fecha_ultima_modificacion,
    calcular_tiempo_registro,
    obtener_estado_accion_generico,
    reordenar_detalle
)

User = get_user_model()


class Etapa4Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.ReadOnlyField()
    usuarios_gore = serializers.SerializerMethodField()
    oficio_inicio_gore = serializers.SerializerMethodField()
    formularios_gore = serializers.SerializerMethodField()
    tipo_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Etapa4
        fields = [
            'id',
            'nombre_etapa',
            'estado',
            'fecha_inicio',
            'calcular_tiempo_transcurrido',
            'plazo_dias',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'usuarios_gore',
            'oficio_inicio_gore',
            'oficio_origen',
            'formularios_gore',
            'tipo_usuario'
        ]

    def get_tipo_usuario(self, obj):
        return {"GORE"}

    def get_ultimo_editor(self, obj):
        return get_ultimo_editor(self, obj)

    def get_fecha_ultima_modificacion(self, obj):
        return get_fecha_ultima_modificacion(self, obj)

    def reordenar_detalle(self, detalle, user):
        return reordenar_detalle(self, detalle, user)

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

    def get_oficio_inicio_gore(self, obj):
        return obtener_estado_accion_generico(
            self,
            id=obj.competencia.etapa4.id,
            condicion=obj.oficio_origen,
            condicion_anterior=obj.usuarios_gore_notificados,
            usuario_grupo='SUBDERE',
            conteo_condicion=1,
            nombre_singular='Subir oficio y su fecha para habilitar formulario GORE',
            accion_usuario_grupo='Subir oficio',
            accion_general='Oficio pendiente',
            accion_finalizada_usuario_grupo='Ver oficio',
            accion_finalizada_general='Ver oficio',
        )

    def get_formularios_gore(self, obj):
        request = self.context.get('request')
        user = self.context['request'].user
        es_usuario_gore = obj.competencia.usuarios_gore.filter(id=user.id).exists()
        regiones = obj.competencia.regiones.all()
        detalle = []

        for region in regiones:
            formulario_gore = FormularioGORE.objects.filter(competencia=obj.competencia, region=region).first()

            if formulario_gore:
                # Verifica si el usuario es GORE y si la región del formulario coincide con la del usuario
                usuario_region_correcta = es_usuario_gore and user.region == region if user.region else False
                estado_revision = usuario_region_correcta and obj.oficio_origen
                estado = 'finalizada' if formulario_gore.formulario_enviado else 'revision' if estado_revision else 'pendiente'
                accion = 'Ver Formulario' if formulario_gore.formulario_enviado else 'Subir Formulario' if usuario_region_correcta else 'Formulario pendiente'

                # Obtener antecedente_adicional_gore y descripcion_antecedente
                antecedente_adicional_gore = request.build_absolute_uri(formulario_gore.antecedente_adicional_gore.url) if formulario_gore.antecedente_adicional_gore else 'No aplica'
                descripcion_antecedente = formulario_gore.descripcion_antecedente if formulario_gore.descripcion_antecedente else 'No aplica'

                detalle_formulario = {
                    "id": formulario_gore.id,
                    "region_id": region.id,
                    "nombre": f"Completar formulario GORE - {region.region}",
                    "estado": estado,
                    "accion": accion,
                    "antecedente_adicional_gore": antecedente_adicional_gore,
                    "descripcion_antecedente": descripcion_antecedente
                }

                if formulario_gore.formulario_enviado:
                    detalle_formulario["registro_tiempo"] = calcular_tiempo_registro(self, obj.fecha_inicio,
                                                                                     formulario_gore.fecha_envio)

                detalle.append(detalle_formulario)

        if len(regiones) <= 1:
            return detalle

        resumen_estado = 'finalizada' if obj.formulario_gore_completo else 'revision'
        resumen_accion = 'Ver formularios' if obj.formulario_gore_completo else 'Formularios pendientes'
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

