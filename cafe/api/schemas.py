from api.serializers.order_serializers import (
    OrderChangeStatusSerializer,
    RevenueSerializer,
)
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, extend_schema_view


class OrderViewExtension(OpenApiViewExtension):
    """Документация для эндпоинтов заказов"""

    target_class = "api.views.order_views.OrderViewSet"

    def view_replacement(self):
        from orders.models import Order

        @extend_schema(tags=["Заказы"])
        @extend_schema_view(
            list=extend_schema(
                summary="Получение списка заказов",
                description="Возвращает список всех заказов.",
            ),
            retrieve=extend_schema(
                summary="Получение информации о конкретном заказе",
                description="Возвращает полную информацию о выбранном заказе.",
            ),
            create=extend_schema(
                summary="Создание заказа",
                description="Добавляет новый заказ в базу данных.",
            ),
            update=extend_schema(
                summary="Обновление информации о заказе",
                description="Обновляет данные существующего заказа.",
            ),
            partial_update=extend_schema(
                summary="Частичное обновление информации о заказе",
                description="Обновляет данные существующего заказа.",
            ),
            destroy=extend_schema(
                summary="Удаление заказа",
                description="Удаляет выбранный заказ из базы данных.",
            ),
            change_status=extend_schema(
                summary="Изменение статуса заказа",
                description="Изменение статуса заказа.",
                request=OrderChangeStatusSerializer,
                responses={201: OrderChangeStatusSerializer},
            ),
            revenue=extend_schema(
                summary="Изменение статуса заказа",
                description="Изменение статуса заказа.",
                responses={200: RevenueSerializer},
            ),
        )
        class Fixed(self.target_class):
            queryset = Order.objects.none()

        return Fixed


class DishViewExtension(OpenApiViewExtension):
    """Документация для эндпоинтов блюд"""

    target_class = "api.views.menu_views.DishReadViewSet"

    def view_replacement(self):
        from menu.models import Dish

        @extend_schema(tags=["Меню"])
        @extend_schema_view(
            list=extend_schema(
                summary="Получение списка блюд",
                description="Возвращает список всех блюд.",
            ),
            retrieve=extend_schema(
                summary="Получение информации о конкретном блюде",
                description="Возвращает полную информацию о выбранном блюде.",
            ),
        )
        class Fixed(self.target_class):
            queryset = Dish.objects.none()

        return Fixed
