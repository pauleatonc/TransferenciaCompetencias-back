from rest_framework.views import APIView
from rest_framework.response import Response

from applications.competencias.api.v1.serializers import OrigenSerializer
from applications.competencias.models import Competencia


class OrigenAPIView(APIView):
    def get(self, request, format=None):
        origenes = [
            {'clave': clave, 'descripcion': descripcion}
            for clave, descripcion in Competencia.ORIGEN
        ]
        serializer = OrigenSerializer(origenes, many=True)
        return Response(serializer.data)
