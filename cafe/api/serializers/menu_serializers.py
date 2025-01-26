from rest_framework import serializers

from menu.models import Dish


class DishReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра меню блюд"""

    class Meta:
        model = Dish
        fields = ("id", "name", "price")
