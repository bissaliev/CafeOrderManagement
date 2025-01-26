from rest_framework.viewsets import ReadOnlyModelViewSet

from api.serializers.menu_serializers import DishReadSerializer
from menu.models import Dish


class DishReadViewSet(ReadOnlyModelViewSet):
    """Просмотр меню блюд"""

    queryset = Dish.objects.filter(is_active=True)
    serializer_class = DishReadSerializer
