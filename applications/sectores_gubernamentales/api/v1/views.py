from ...models import SectorGubernamental
#
from rest_framework.generics import ListAPIView
#
from .serializer import SectorGubernamentalSerializer


class SectorGubernamentalView(ListAPIView):

    serializer_class = SectorGubernamentalSerializer

    def get_queryset(self):
        return SectorGubernamental.objects.all()
