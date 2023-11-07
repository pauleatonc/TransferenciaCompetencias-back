from ...models import Region, Comuna
#
from rest_framework.generics import ListAPIView
#
from .serializer import RegionComunaSerializer


class RegionComunaView(ListAPIView):

    serializer_class = RegionComunaSerializer

    def get_queryset(self):
        return Region.objects.all()
