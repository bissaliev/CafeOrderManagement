from orders.models import Order, OrderItem
from rest_framework import serializers


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения позиций заказа"""

    dish = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "dish", "price", "quantity")


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Создание позиций заказа"""

    class Meta:
        model = OrderItem
        fields = ("id", "dish", "quantity")


class OrderBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для заказов"""

    total_price = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        source="get_total_price",
        read_only=True,
    )

    class Meta:
        model = Order
        fields = ("id", "table_number", "status", "total_price", "items")


class OrderReadSerializer(OrderBaseSerializer):
    """Просмотр заказов"""

    items = OrderItemReadSerializer(many=True)


class OrderCreateSerializer(OrderBaseSerializer):
    items = OrderItemCreateSerializer(many=True)

    def create(self, validated_data: dict):
        items = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItem.objects.create(order=order, **item)
        return order

    def _save_items(self, instance: Order, items_data: list[dict]):
        """Обновление позиций в заказе"""
        items_in_db = {i.dish_id: i for i in instance.items.all()}
        for item_data in items_data:
            dish_id = item_data["dish"].id
            if dish_id in items_in_db:
                item = items_in_db.pop(item_data["dish"].id)
                item.quantity = item_data["quantity"]
                item.save()
            else:
                OrderItem.objects.create(order=instance, **item_data)
        OrderItem.objects.filter(dish_id__in=items_in_db.keys()).delete()

    def update(self, instance: Order, validated_data: dict):
        instance.table_number = validated_data.get(
            "table_number", instance.table_number
        )
        instance.status = validated_data.get("status", instance.status)

        if "items" in validated_data:
            items_data = validated_data.pop("items")
            self._save_items(instance, items_data)

        instance.save()

        return instance


class OrderChangeStatusSerializer(serializers.ModelSerializer):
    """Сериализатор для смены статуса заказа"""

    class Meta:
        model = Order
        fields = ("status",)


class RevenueSerializer(serializers.Serializer):
    """
    Сериализатор для вывода выручки за оплаченные заказы за периоды:
    Сегодня, Неделю, Месяц, Все время
    """

    today = serializers.DecimalField(max_digits=8, decimal_places=2)
    week = serializers.DecimalField(max_digits=8, decimal_places=2)
    month = serializers.DecimalField(max_digits=8, decimal_places=2)
    all_time = serializers.DecimalField(max_digits=8, decimal_places=2)
