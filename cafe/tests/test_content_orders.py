from django.test import TestCase
from django.urls import reverse

from menu.models import Dish
from orders.models import Order, OrderItem


class TestOrderContent(TestCase):
    """Тестирование контента приложения orders"""

    name_list = "orders:order_list"
    name_create = "orders:order_create"
    name_edit = "orders:order_edit"
    name_delete = "orders:order_delete"
    name_update_status = "orders:order_update_status"
    name_revenue = "orders:revenue"

    @classmethod
    def setUpTestData(cls):
        cls.dish = Dish.objects.create(
            name="test dish", description="test description", price=999.99
        )
        cls.order = Order.objects.create(table_number="1")
        OrderItem.objects.create(
            order=cls.order, dish=cls.dish, price=200.00, quantity=2
        )

    def test_content_order_list_render_is_correct(self):
        """Проверка отображения страницы списка заказов"""
        url = reverse(self.name_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertEqual(len(object_list), 1)
        self.assertEqual(object_list[0].id, self.order.id)

    def test_form_in_page(self):
        """Формы присутствуют на страницах создания и обновления заказов"""
        urls = (
            reverse(self.name_create),
            reverse(self.name_edit, args=[self.order.id]),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn("form", response.context)
                self.assertIn("formset", response.context)

    def test_content_revenue_render_is_correct(self):
        """Проверка отображения страницы расчета выручки"""
        variables = ("all_time", "today", "week", "month")
        url = reverse(self.name_revenue)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("revenue_period", response.context)
        for variable in variables:
            with self.subTest(variable=variable):
                self.assertIn(variable, response.context["revenue_period"])
