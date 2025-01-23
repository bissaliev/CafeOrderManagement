from django.test import TestCase
from django.urls import reverse
from menu.models import Dish
from orders.models import Order, OrderItem


class TestOrderLogic(TestCase):
    """Тестирования логики приложения orders"""

    name_list = "orders:order_list"
    name_create = "orders:order_create"
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

    def test_update_status_of_non_existent_order(self):
        """
        Обновление статуса для несуществующего заказа возвращает ошибку 404
        """
        url = reverse(self.name_update_status, args=[100])
        data = {"status": "PAID"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_delete_order_is_correct(self):
        """Заказ корректно удаляется"""
        url = reverse(self.name_delete, args=[self.order.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse(self.name_list))
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_non_existent_order(self):
        """Удаление несуществующего заказа возвращает ошибку 404"""
        url = reverse(self.name_delete, args=[100])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_order_search_by_table_number(self):
        """Корректность поиска заказа по номеру столика"""
        order = Order.objects.create(table_number=2)
        url = reverse(self.name_list)
        response = self.client.get(
            url, data={"table_number": order.table_number}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 1)
        request_order = response.context["object_list"][0]
        self.assertEqual(request_order.id, order.id)

    def test_order_search_by_non_exists_table_number(self):
        """По несуществующему номеру столика возвращается нулевой результат"""
        url = reverse(self.name_list)
        response = self.client.get(url, data={"table_number": 100})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 0)

    def test_filter_order_by_status(self):
        """Заказы корректно фильтруются по статусам"""
        url = reverse(self.name_list)
        response = self.client.get(url, data={"status": self.order.status})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 1)

    def test_filter_order_by_non_existent_status(self):
        """
        Фильтрация по несуществующему статусу возвращает нулевой результат
        """
        url = reverse(self.name_list)
        response = self.client.get(url, data={"status": "NOT EXISTS"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 0)

    def test_content_revenue(self):
        """Корректность вычисление выручки"""
        url = reverse(self.name_revenue)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("revenue_period", response.context)
        self.assertIn("all_time", response.context["revenue_period"])
        self.assertIn("today", response.context["revenue_period"])
        self.assertIn("week", response.context["revenue_period"])
        self.assertIn("month", response.context["revenue_period"])

        self.assertEqual(response.context["revenue_period"]["all_time"], 0)
        self.assertEqual(response.context["revenue_period"]["today"], 0)
        self.assertEqual(response.context["revenue_period"]["week"], 0)
        self.assertEqual(response.context["revenue_period"]["month"], 0)

        self.order.status = Order.Status.PAID
        self.order.save()
        expected = sum(i.price * i.quantity for i in self.order.items.all())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["revenue_period"]["all_time"], expected
        )
        self.assertEqual(response.context["revenue_period"]["today"], expected)
        self.assertEqual(response.context["revenue_period"]["week"], expected)
        self.assertEqual(response.context["revenue_period"]["month"], expected)
