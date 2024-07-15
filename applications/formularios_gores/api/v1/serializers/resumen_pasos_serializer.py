from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.formularios_gores.models import PasoBase, Paso1, Paso2, Paso3, FormularioGORE

User = get_user_model()


class PasoBaseSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = PasoBase
        fields = [
            'pk',
            'nombre_paso',
            'numero_paso',
            'avance',
            'completado',
            'estado_stepper',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso1ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso1


class Paso2ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso2


class Paso3ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso3


class ResumenFormularioSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()
    region_nombre = serializers.SerializerMethodField()
    paso1_gore = Paso1ResumenSerializer(read_only=True)
    paso2_gore = Paso2ResumenSerializer(read_only=True)
    paso3_gore = Paso3ResumenSerializer(read_only=True)
    formulario_completo = serializers.SerializerMethodField()
    antecedente_adicional_gore = serializers.FileField(required=False, allow_null=True)
    download_antecedente_adicional_gore = serializers.SerializerMethodField()
    delete_antecedente_adicional_gore = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = FormularioGORE
        fields = [
            'id',
            'competencia_nombre',
            'region_nombre',
            'formulario_enviado',
            'fecha_envio',
            'intento_envio',
            'paso1_gore',
            'paso2_gore',
            'paso3_gore',
            'formulario_completo',
            'antecedente_adicional_gore',
            'download_antecedente_adicional_gore',
            'delete_antecedente_adicional_gore',
            'descripcion_antecedente'
        ]

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre if obj.competencia else None

    def get_region_nombre(self, obj):
        return obj.region.region if obj.region else None

    def get_formulario_completo(self, obj):
        # Revisa si todos los pasos están completados
        pasos_completados = [
            obj.paso1.completado if hasattr(obj, 'paso1') else False,
            obj.paso2.completado if hasattr(obj, 'paso2') else False,
            obj.paso3.completado if hasattr(obj, 'paso3') else False,
        ]
        # Retorna True si todos los pasos están completados, False en caso contrario
        return all(pasos_completados)

    def update(self, instance, validated_data):
        if validated_data.get('delete_antecedente_adicional_gore'):
            instance.delete_file()
        validated_data.pop('delete_antecedente_adicional_gore', None)
        return super().update(instance, validated_data)

    def get_download_antecedente_adicional_gore(self, obj):
        request = self.context.get('request')
        if obj.antecedente_adicional_gore and request:
            return request.build_absolute_uri(obj.antecedente_adicional_gore.url)
        return None