from applications.regioncomuna.models import Region
#
from rest_framework.generics import ListAPIView
from django.db.models import Case, When, Value, IntegerField
#
from .serializer import RegionSerializer


class RegionView(ListAPIView):

    serializer_class = RegionSerializer

    def get_queryset(self):
        orden_personalizado = Case(
            When(id=1, then=Value(1)),
            When(id=2, then=Value(2)),
            When(id=3, then=Value(3)),
            When(id=4, then=Value(4)),
            When(id=5, then=Value(5)),
            When(id=6, then=Value(6)),
            When(id=16, then=Value(7)),
            When(id=7, then=Value(8)),
            When(id=8, then=Value(9)),
            When(id=9, then=Value(10)),
            When(id=10, then=Value(11)),
            When(id=11, then=Value(12)),
            When(id=12, then=Value(13)),
            When(id=13, then=Value(14)),
            When(id=14, then=Value(15)),
            When(id=15, then=Value(16)),
            When(id=17, then=Value(17)),
            default=Value(18),
            output_field=IntegerField()
        )

        # Usar `annotate()` para agregar el campo de orden personalizado y luego ordenar por ese campo
        queryset = Region.objects.annotate(orden_personalizado=orden_personalizado).order_by('orden_personalizado')
        return queryset
