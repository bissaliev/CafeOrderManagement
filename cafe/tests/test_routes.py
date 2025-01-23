from django.test import TestCase
from django.urls import reverse
from menu.models import Dish
from orders.models import Order, OrderItem


class TestMenuRoutes(TestCase):
    """Тестирование маршрутов приложения menu"""

    @classmethod
    def setUpTestData(cls):
        cls.dish = Dish.objects.create(
            name="test dish", description="test description", price=999.99
        )

    def test_pages_is_available(self):
        """Проверка доступности страниц"""
        reverse_names = (
            ("menu:dish_list", None),
            ("menu:dish_detail", [self.dish.id]),
        )
        for name, arg in reverse_names:
            url = reverse(name, args=arg)
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, 200, "Статус ответа должен быть 200"
                )


class TestOrderRoutes(TestCase):
    """Тестирования маршрутов приложения orders"""

    @classmethod
    def setUpTestData(cls):
        cls.dish = Dish.objects.create(
            name="test dish", description="test description", price=999.99
        )
        cls.order = Order.objects.create(table_number="1")
        OrderItem.objects.create(order=cls.order, dish=cls.dish)

    def test_pages_is_available(self):
        """Проверка доступности страниц"""
        reverse_names = (
            ("orders:order_list", None),
            ("orders:order_create", None),
            ("orders:revenue", None),
        )
        for name, arg in reverse_names:
            url = reverse(name, args=arg)
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
