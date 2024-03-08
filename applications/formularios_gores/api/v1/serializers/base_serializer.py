from rest_framework import serializers

from applications.formularios_sectoriales.models import FormularioSectorial
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()

class FormularioGOREDetailSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()
    competencia_id = serializers.SerializerMethodField()
    region_nombre = serializers.SerializerMethodField()
    plazo_dias = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.SerializerMethodField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'competencia_nombre',
            'competencia_id',
            'region_nombre',
            'plazo_dias',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
            'fecha_envio',
            'formulario_enviado',
            'intento_envio'
        ]

    def get_competencia_nombre(self, obj):
        if obj.competencia:
            return obj.competencia.nombre
        return None

    def get_competencia_id(self, obj):
        if obj.competencia:
            return obj.competencia.id
        return None

    def get_region_nombre(self, obj):
        if obj.region:
            return obj.region.region
        return None

    def get_etapa4(self, obj):
        return obj.competencia.etapa4

    def get_plazo_dias(self, obj):
        etapa4 = self.get_etapa4(obj)
        return etapa4.plazo_dias if etapa4 else None

    def get_calcular_tiempo_transcurrido(self, obj):
        etapa4 = self.get_etapa4(obj)
        if etapa4:
            return etapa4.calcular_tiempo_transcurrido()
        return {'dias': 0, 'horas': 0, 'minutos': 0}

    def get_ultimo_editor(self, obj):
        etapa4 = self.get_etapa4(obj)
        historial = etapa4.historical.all().order_by('-history_date')
        for record in historial:
            if record.history_user:
                return {
                    'nombre_completo': record.history_user.nombre_completo,
                    'perfil': record.history_user.perfil
                }
        return None

    def get_fecha_ultima_modificacion(self, obj):
        try:
            etapa4 = self.get_etapa4(obj)
            ultimo_registro = etapa4.historical.latest('history_date')
            if ultimo_registro:
                fecha_local = timezone.localtime(ultimo_registro.history_date)
                return fecha_local.strftime('%d/%m/%Y - %H:%M')
            return None
        except obj.historical.model.DoesNotExist:
            return None