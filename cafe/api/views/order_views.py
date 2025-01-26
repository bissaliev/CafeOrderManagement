from api.serializers.order_serializers import (
    OrderChangeStatusSerializer,
    OrderCreateSerializer,
    OrderReadSerializer,
    RevenueSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from orders.models import Order
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related("items", "items__dish")
    serializer_class = OrderReadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("status", "table_number")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return super().get_serializer_class()
        return OrderCreateSerializer

    @action(methods=["PATCH"], detail=True)
    def change_status(self, request, pk=None):
        """Смена статуса заказа"""
        serializer = OrderChangeStatusSerializer(
            self.get_object(), data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(methods=["GET"], detail=False)
    def revenue(self, request):
        """Получение выручки"""
        revenue = Order.get_total_revenue_for_periods()
        serializer = RevenueSerializer(data=revenue)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
