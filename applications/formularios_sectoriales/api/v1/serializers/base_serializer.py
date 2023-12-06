from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

User = get_user_model()


class CompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = [
            'nombre',
        ]


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGubernamental
        fields = ('nombre',)


class FormularioSectorialDetailSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    plazo_dias = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.SerializerMethodField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'competencia_nombre',
            'sector_nombre',
            'nombre',
            'plazo_dias',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
        ]

    def get_competencia_nombre(self, obj):
        if obj.competencia:
            return obj.competencia.nombre
        return None

    def get_sector_nombre(self, obj):
        if obj.sector:
            return obj.sector.nombre
        return None

    def get_etapa2(self, obj):
        return obj.competencia.etapa2_set.first()

    def get_plazo_dias(self, obj):
        etapa2 = self.get_etapa2(obj)
        return etapa2.plazo_dias if etapa2 else None

    def get_calcular_tiempo_transcurrido(self, obj):
        etapa2 = self.get_etapa2(obj)
        if etapa2:
            return etapa2.calcular_tiempo_transcurrido()
        return {'dias': 0, 'horas': 0, 'minutos': 0}

    def get_ultimo_editor(self, obj):
        etapa2 = self.get_etapa2(obj)
        historial = etapa2.historical.all().order_by('-history_date')
        for record in historial:
            if record.history_user:
                return {
                    'nombre_completo': record.history_user.nombre_completo,
                    'perfil': record.history_user.perfil
                }
        return None

    def get_fecha_ultima_modificacion(self, obj):
        try:
            etapa2 = self.get_etapa2(obj)
            ultimo_registro = etapa2.historical.latest('history_date')
            if ultimo_registro:
                fecha_local = timezone.localtime(ultimo_registro.history_date)
                return fecha_local.strftime('%d/%m/%Y - %H:%M')
            return None
        except obj.historical.model.DoesNotExist:
            return None