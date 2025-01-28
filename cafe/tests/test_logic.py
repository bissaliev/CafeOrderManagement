from django.test import TestCase
from django.urls import reverse

from menu.models import Dish
from orders.models import Order, OrderItem


class TestOrderLogic(TestCase):
    """Тестирования логики приложения orders"""

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

    def test_order_create_is_correct(self):
        """Проверка корректности создания заказов"""
        data = {
            "table_number": 1,
            "items-TOTAL_FORMS": ["1"],
            "items-INITIAL_FORMS": ["0"],
            "items-0-id": [""],
            "items-0-dish": [f"{self.dish.id}"],
            "items-0-quantity": ["2"],
        }
        count_orders = Order.objects.count()
        count_orderitem = OrderItem.objects.count()
        url = reverse(self.name_create)
        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse(self.name_list))
        self.assertEqual(Order.objects.count(), count_orders + 1)
        self.assertEqual(OrderItem.objects.count(), count_orderitem + 1)

    def test_create_order_without_dish(self):
        """Заказ не создается без указания хотя бы одной позиции блюда"""
        data = {"table_number": 1}
        count_orders = Order.objects.count()
        url = reverse(self.name_create)
        self.client.post(url, data=data)
        self.assertEqual(Order.objects.count(), count_orders)

    def test_edit_order_is_correct_with_replacement(self):
        """Проверка редактирования заказа с заменой позиции на новую"""
        new_dish = Dish.objects.create(name="new_dish", price=200.00)
        data = {
            "table_number": 1,
            "items-TOTAL_FORMS": ["1"],
            "items-INITIAL_FORMS": ["1"],
            "items-0-id": [f"{self.order.items.first().id}"],
            "items-0-dish": [f"{new_dish.id}"],
            "items-0-quantity": ["3"],
        }
        count_orders = Order.objects.count()
        url = reverse(self.name_edit, args=[self.order.id])
        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse(self.name_list))
        self.assertEqual(Order.objects.count(), count_orders)
        self.assertEqual(self.order.items.count(), 1)

    def test_edit_order_is_correct_with_addition(self):
        """Проверка редактирования заказа с добавлением новой позиции"""
        new_dish = Dish.objects.create(name="new_dish", price=200.00)
        item = self.order.items.first()
        data = {
            "table_number": 1,
            "items-TOTAL_FORMS": ["2"],
            "items-INITIAL_FORMS": ["1"],
            "items-0-id": [f"{item.id}"],
            "items-0-dish": [f"{item.dish.id}"],
            "items-0-quantity": [f"{item.quantity}"],
            "items-1-id": [""],
            "items-1-dish": [f"{new_dish.id}"],
            "items-1-quantity": ["3"],
        }
        count_orders = Order.objects.count()
        url = reverse(self.name_edit, args=[self.order.id])
        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse(self.name_list))
        self.assertEqual(Order.objects.count(), count_orders)
        self.assertEqual(self.order.items.count(), 2)

    def test_update_order_status(self):
        """Статус заказа корректно обновляется"""
        url = reverse(self.name_update_status, args=[self.order.id])
        data = {"status": Order.Status.PAID}
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse(self.name_list))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, data["status"])

    def test_update_order_status_invalid_data(self):
        """При указании некорректного статусы вызывается исключение"""
        url = reverse(self.name_update_status, args=[self.order.id])
        data = {"status": "NOT EXISTS"}
        with self.assertRaises(ValueError):
            self.client.post(url, data=data)

    def test_delete_order_is_correct(self):
        """Заказ корректно удаляется"""
        url = reverse(self.name_delete, args=[self.order.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse(self.name_list))
        self.assertEqual(Order.objects.count(), 0)

    def test_accessing_non_existent_order(self):
        """
        Обращения к несуществующему заказу при удалении, редактирование,
        обновление статуса возвращает ошибку 404
        """
        reverse_names = (
            self.name_delete,
            self.name_edit,
            self.name_update_status,
        )
        for reverse_name in reverse_names:
            url = reverse(reverse_name, args=[100])
            with self.subTest(url=url):
                response = self.client.post(url)
                self.assertEqual(response.status_code, 404)

    def test_filtering_and_searching_orders(self):
        """Тестирование фильтрации по статусу и поиска по номеру стола"""
        url = reverse(self.name_list)
        field_value_expected = (
            ("status", Order.Status.PAID, 0),
            ("status", self.order.status, 1),
            ("table_number", "2", 0),
            ("table_number", self.order.table_number, 1),
        )
        for field, value, exp in field_value_expected:
            with self.subTest(field=field):
                response = self.client.get(url, data={field: value})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context["object_list"]), exp)

    def test_content_revenue(self):
        """Корректность вычисление выручки для оплаченных заказов"""
        url = reverse(self.name_revenue)
        variables = ("all_time", "today", "week", "month")
        for status in Order.Status:
            self.order.status = status.value
            self.order.save()
            revenue_from_db = Order.get_total_revenue_for_periods()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("revenue_period", response.context)
            for variable in variables:
                with self.subTest(status=status, variable=variable):
                    self.assertEqual(
                        revenue_from_db[variable],
                        response.context["revenue_period"][variable],
                    )
