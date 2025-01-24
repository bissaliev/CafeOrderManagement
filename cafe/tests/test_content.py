from django.test import TestCase
from django.urls import reverse
from menu.models import Dish
from orders.models import Order, OrderItem


class TestMenuContent(TestCase):
    """Тестирование контента приложения menu"""

    url_name_list = "menu:dish_list"
    url_name_detail = "menu:dish_detail"
    pages_count = 12

    @classmethod
    def setUpTestData(cls):
        cls.dishes = Dish.objects.bulk_create(
            [
                Dish(
                    name=f"dish-{i}",
                    description=f"test-dish-{i}",
                    price=999.99,
                )
                for i in range(cls.pages_count + 1)
            ]
        )

    def test_menu_list_render_is_correct(self):
        """Проверка отображения списка блюд"""
        url = reverse(self.url_name_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertEqual(len(object_list), self.pages_count)
        self.assertEqual(object_list[0].id, self.dishes[0].id)
        response = self.client.get(f"{url}?page=2")
        self.assertEqual(response.status_code, 200)
        object_list = response.context["object_list"]
        self.assertEqual(len(object_list), 1)

    def test_menu_detail_render_is_correct(self):
        """Проверка отображения подробного описания блюда"""
        url = reverse(self.url_name_detail, args=[self.dishes[0].id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("object", response.context)
        object = response.context["object"]
        self.assertEqual(object.name, self.dishes[0].name)


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

    def test_content_order_create_render_is_correct(self):
        """Проверка отображения страницы создания заказов"""
        url = reverse(self.name_create)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("formset", response.context)

    def test_content_order_edit_render_is_correct(self):
        """Проверка отображения страницы редактирования заказов"""
        url = reverse(self.name_edit, args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("formset", response.context)

    def test_content_revenue_render_is_correct(self):
        """Проверка отображения страницы расчета выручки"""
        url = reverse(self.name_revenue)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("revenue_period", response.context)
        self.assertIn("all_time", response.context["revenue_period"])
        self.assertIn("today", response.context["revenue_period"])
        self.assertIn("week", response.context["revenue_period"])
        self.assertIn("month", response.context["revenue_period"])
