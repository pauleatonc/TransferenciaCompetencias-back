from applications.sectores_gubernamentales.models import Ministerio
#
from rest_framework.generics import ListAPIView
#
from .serializer import MinisterioSerializer


class SectorGubernamentalView(ListAPIView):

    serializer_class = MinisterioSerializer

    def get_queryset(self):
        return Ministerio.objects.all()
