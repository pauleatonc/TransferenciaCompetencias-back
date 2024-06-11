from django.db import transaction
from rest_framework import serializers
from applications.competencias.models import Competencia, Ambito, CompetenciaAgrupada
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

from applications.etapas.api.v1.serializers import Etapa1Serializer, Etapa2Serializer, Etapa3Serializer, \
    Etapa4Serializer, Etapa5Serializer

User = get_user_model()


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGubernamental
        fields = ('id', 'nombre')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'region')


class CompetenciaAgrupadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenciaAgrupada
        fields = ('id', 'nombre', 'competencias', 'modalidad_ejercicio')


class UsuarioSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.SerializerMethodField()
    region_nombre = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nombre_completo', 'email', 'sector_nombre', 'region_nombre')

    def get_sector_nombre(self, obj):
        if obj.sector:
            return obj.sector.nombre
        return None

    def get_region_nombre(self, obj):
        if obj.region:
            return obj.region.region
        return None


class CompetenciaListSerializer(serializers.ModelSerializer):

    ambito = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    origen = serializers.SerializerMethodField()
    class Meta:
        model = Competencia
        fields = ['id', 'nombre', 'ambito', 'estado', 'origen', 'agrupada']

    def get_ambito(self, obj):
        return obj.ambito_competencia.nombre if obj.ambito_competencia else None

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre if obj.competencia else None

    def get_estado(self, obj):
        return obj.get_estado_display()

    def get_origen(self, obj):
        return obj.get_origen_display()


class CompetenciaListAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
        ]


class CompetenciaHomeListSerializer(serializers.ModelSerializer):

    etapas_info = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    ambito_definitivo_competencia = serializers.SerializerMethodField()
    ambito_competencia_origen = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
            'etapas_info',
            'tiempo_transcurrido',
            'estado',
            'ambito_definitivo_competencia',
            'ambito_competencia_origen',
            'fecha_fin',
            'recomendacion_transferencia',
            'agrupada'
        ]

    def get_estado(self, obj):
        return obj.get_estado_display()

    def get_ambito_definitivo_competencia(self, obj):
        return obj.ambito_definitivo_competencia.nombre if obj.ambito_definitivo_competencia else None

    def get_ambito_competencia_origen(self, obj):
        return obj.ambito_competencia.nombre if obj.ambito_competencia else None

    def get_etapas_info(self, obj):
        return obtener_informacion_etapas(obj)


class CompetenciaCreateSerializer(serializers.ModelSerializer):
    competencias_agrupadas = CompetenciaAgrupadaSerializer(many=True, required=False)
    sectores = serializers.PrimaryKeyRelatedField(many=True, queryset=SectorGubernamental.objects.all(), required=False)
    regiones = serializers.PrimaryKeyRelatedField(many=True, queryset=Region.objects.all(), required=False)
    regiones_recomendadas = serializers.PrimaryKeyRelatedField(many=True, queryset=Region.objects.all(), required=False)
    usuarios_subdere = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(groups__name='SUBDERE'), required=False)
    usuarios_dipres = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(groups__name='DIPRES'), required=False)
    usuarios_sectoriales = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(groups__name='Usuario Sectorial'), required=False)
    usuarios_gore = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(groups__name='GORE'), required=False)

    class Meta:
        model = Competencia
        fields = '__all__'

    def create(self, validated_data):
        # Extraer los campos de ManyToMany del validated_data
        sectores_data = validated_data.pop('sectores', None)
        regiones_data = validated_data.pop('regiones', None)
        regiones_recomendadas_data = validated_data.pop('regiones_recomendadas', None)
        usuarios_subdere_data = validated_data.pop('usuarios_subdere', None)
        usuarios_dipres_data = validated_data.pop('usuarios_dipres', None)
        usuarios_sectoriales_data = validated_data.pop('usuarios_sectoriales', None)
        usuarios_gore_data = validated_data.pop('usuarios_gore', None)

        # Crear la instancia de Competencia sin los campos de muchos a muchos
        competencia = Competencia.objects.create(**validated_data)

        # Asignar los sectores y regiones usando set()
        if sectores_data:
            competencia.sectores.set(sectores_data)
        if regiones_data:
            competencia.regiones.set(regiones_data)
        if regiones_recomendadas_data:
            competencia.regiones_recomendadas.set(regiones_recomendadas_data)

        # Asignar los usuarios usando set()
        if usuarios_subdere_data:
            competencia.usuarios_subdere.set(usuarios_subdere_data)
        if usuarios_dipres_data:
            competencia.usuarios_dipres.set(usuarios_dipres_data)
        if usuarios_sectoriales_data:
            competencia.usuarios_sectoriales.set(usuarios_sectoriales_data)
        if usuarios_gore_data:
            competencia.usuarios_gore.set(usuarios_gore_data)

        return competencia


class CompetenciaUpdateSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    plazo_formulario_sectorial = serializers.IntegerField(required=False)
    plazo_formulario_gore = serializers.IntegerField(required=False)
    sectores = serializers.PrimaryKeyRelatedField(many=True, queryset=SectorGubernamental.objects.all(), required=False)
    regiones = serializers.PrimaryKeyRelatedField(many=True, queryset=Region.objects.all(), required=False)

    class Meta:
        model = Competencia
        fields = '__all__'
        extra_kwargs = {'creado_por': {'read_only': True}}


def obtener_informacion_etapas(competencia):
    etapas_info = {}
    for i in range(1, 6):
        etapa_model = globals().get(f'Etapa{i}')
        if etapa_model:
            etapa = etapa_model.objects.filter(competencia=competencia).first()
            if etapa:
                etapas_info[f'Etapa{i}'] = {
                    'nombre': etapa.nombre_etapa,
                    'estado': etapa.get_estado_display()
                }
    return etapas_info


class CompetenciaDetailSerializer(serializers.ModelSerializer):
    etapa1 = Etapa1Serializer()
    etapa2 = Etapa2Serializer()
    etapa3 = Etapa3Serializer()
    etapa4 = Etapa4Serializer()
    etapa5 = Etapa5Serializer()
    usuarios_subdere = UsuarioSerializer(many=True, read_only=True)
    usuarios_dipres = UsuarioSerializer(many=True, read_only=True)
    usuarios_sectoriales = UsuarioSerializer(many=True, read_only=True)
    usuarios_gore = UsuarioSerializer(many=True, read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    sectores = SectorSerializer(many=True, read_only=True)
    regiones = RegionSerializer(many=True, read_only=True)
    resumen_competencia = serializers.SerializerMethodField()
    competencias_agrupadas = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    ambito_definitivo_competencia = serializers.SerializerMethodField()
    ambito_competencia_origen = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
            'agrupada',
            'resumen_competencia',
            'competencias_agrupadas',
            'sectores',
            'regiones',
            'origen',
            'ambito_competencia',
            'oficio_origen',
            'fecha_inicio',
            'plazo_formulario_sectorial',
            'plazo_formulario_gore',
            'etapa1',
            'etapa2',
            'etapa3',
            'etapa4',
            'etapa5',
            'tiempo_transcurrido',
            'usuarios_subdere',
            'usuarios_dipres',
            'usuarios_sectoriales',
            'usuarios_gore',
            'imprimir_formulario_final',

            #campos de finalizada
            'fecha_fin',
            'estado',
            'ambito_competencia_origen',
            'ambito_definitivo_competencia',
            'recomendacion_transferencia'

        ]

    def get_tiempo_transcurrido(self, obj):
        return obj.tiempo_transcurrido()

    def get_resumen_competencia(self, obj):
        etapas_info = obtener_informacion_etapas(obj)
        return {
            'id': obj.id,
            'nombre': obj.nombre,
            'etapas_info': etapas_info,
            'tiempo_transcurrido': obj.tiempo_transcurrido()
        }

    def get_estado(self, obj):
        return obj.get_estado_display()

    def get_ambito_definitivo_competencia(self, obj):
        return obj.ambito_definitivo_competencia.nombre if obj.ambito_definitivo_competencia else None

    def get_ambito_competencia_origen(self, obj):
        return obj.ambito_competencia.nombre if obj.ambito_competencia else None

    def get_competencias_agrupadas(self, obj):
        if obj.agrupada:
            competencias_agrupadas = obj.competencias_agrupadas.all()
            return CompetenciaAgrupadaSerializer(competencias_agrupadas, many=True).data
        return []


class AmbitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambito
        fields = ('id', 'nombre')


class OrigenSerializer(serializers.Serializer):
    clave = serializers.CharField(max_length=2)
    descripcion = serializers.CharField(max_length=30)
