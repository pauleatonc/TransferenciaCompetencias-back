from ...models import Region, Comuna
#
from rest_framework.generics import ListAPIView
#
from .serializer import RegionSerializer


class RegionView(ListAPIView):

    serializer_class = RegionSerializer

    def get_queryset(self):
        return Region.objects.all()
