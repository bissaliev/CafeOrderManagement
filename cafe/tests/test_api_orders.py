from decimal import Decimal

from django.urls import reverse
from menu.models import Dish
from orders.models import Order, OrderItem
from rest_framework.test import APITestCase


class TestOrderAPI(APITestCase):
    """Тестирование API Order"""

    name_list = "api:orders-list"
    name_detail = "api:orders-detail"
    name_change_status = "api:orders-change-status"
    name_revenue = "api:orders-revenue"

    @classmethod
    def setUpTestData(cls):
        cls.dish = Dish.objects.create(
            name="test dish", description="testing", price=999
        )
        cls.order = Order.objects.create(table_number="1")
        OrderItem.objects.create(order=cls.order, dish=cls.dish, quantity=1)

    def test_get_orders_list(self):
        """Получение списка заказов"""
        fields = ("id", "table_number", "status", "total_price", "items")
        url = reverse(self.name_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertIn("results", content)
        self.assertEqual(len(content["results"]), 1)
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, content["results"][0])
        self.assertEqual(content["results"][0]["id"], self.order.id)

    def test_get_order(self):
        """Получение заказа по id"""
        fields = ("id", "table_number", "status", "total_price", "items")
        url = reverse(self.name_detail, args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.json()
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, content)
        self.assertEqual(content["id"], self.order.id)

    def test_get_non_existent_order(self):
        """Получение несуществующего заказа возвращает ошибку 404"""
        url = reverse(self.name_detail, args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_order_is_correct(self):
        """Создание заказа выполняется корректно с валидными данными"""
        data = {
            "table_number": "2",
            "items": [
                {
                    "dish": self.dish.id,
                    "quantity": 1,
                },
            ],
        }
        url = reverse(self.name_list)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_order_is_correct2(self):
        """
        Создание заказа при указании одинаковых блюд сохраняет блюда в одну
        позицию с суммированием количества
        """
        data = {
            "table_number": "2",
            "items": [
                {
                    "dish": self.dish.id,
                    "quantity": 1,
                },
                {
                    "dish": self.dish.id,
                    "quantity": 1,
                },
            ],
        }
        url = reverse(self.name_list)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        order = Order.objects.filter(table_number=data["table_number"]).first()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)

    def test_create_order_with_invalid_data(self):
        """Создание заказа с невалидными данными"""
        data = {
            "table_number": 2,
            "items": [
                {
                    "dish": self.dish.id,
                    "quantity": 1,
                },
            ],
        }
        invalid_data = (
            {"status": "NOT STATUS"},
            {"items": [{"dish": self.dish.id, "quantity": 0}]},
            {"items": [{"dish": 100, "quantity": 1}]},
        )

        for data in invalid_data:
            field, value = list(data.keys())[0], list(data.values())[0]
            with self.subTest(field=field):
                data[field] = value
                url = reverse(self.name_list)
                response = self.client.post(url, data=data, format="json")
                self.assertEqual(response.status_code, 400)

    def test_update_order_is_correct(self):
        """Корректно изменяются данные заказа"""
        new_dish = Dish.objects.create(
            name="dish test 2", description="testing", price=100
        )
        url = reverse(self.name_detail, args=[self.order.id])
        new_data = {
            "table_number": "2",
            "items": [
                {
                    "dish": new_dish.id,
                    "quantity": 1,
                },
            ],
        }
        response = self.client.patch(url, data=new_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.table_number, new_data["table_number"])
        self.assertEqual(self.order.items.count(), 1)

    def test_update_order_is_correct_quantity(self):
        """
        Изменение заказа при указании одинаковых блюд сохраняет блюда в одну
        позицию с суммирование количества
        """
        url = reverse(self.name_detail, args=[self.order.id])
        new_quantity = 5
        new_data = {
            "table_number": "2",
            "items": [
                {
                    "dish": self.dish.id,
                    "quantity": new_quantity,
                },
                {
                    "dish": self.dish.id,
                    "quantity": new_quantity,
                },
            ],
        }
        response = self.client.patch(url, data=new_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.table_number, new_data["table_number"])
        self.assertEqual(self.order.items.count(), 1)
        order_item = OrderItem.objects.filter(order=self.order).first()
        self.assertEqual(order_item.quantity, new_quantity * 2)

    def test_change_status_orders(self):
        """Изменение статуса выполняется корректно с валидными данными"""
        new_status = Order.Status.PAID
        url = reverse(self.name_change_status, args=[self.order.id])
        response = self.client.patch(
            url, data={"status": new_status}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, new_status)

    def test_change_status_orders_with_invalid_status(self):
        """Изменение статуса заказа с указанием невалидного значения статуса"""
        new_status = "NON STATUS"
        url = reverse(self.name_change_status, args=[self.order.id])
        response = self.client.patch(
            url, data={"status": new_status}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_get_revenue(self):
        """Корректно возвращается расчет выручки"""
        url = reverse(self.name_revenue)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        revenue = response.json()
        for key, value in revenue.items():
            with self.subTest(key=key):
                self.assertEqual(Decimal(value), Decimal("0.00"))

        self.order.status = Order.Status.PAID
        self.order.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        revenue = response.json()
        revenue_from_db = Order.get_total_revenue_for_periods()
        for key, value in revenue.items():
            with self.subTest(key=key):
                self.assertEqual(Decimal(value), revenue_from_db[key])

    def test_filter_orders_by_status(self):
        url = reverse(self.name_list)
        data = {"status": Order.Status.PENDING}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        objects = response.json()["results"]
        self.assertEqual(len(objects), 1)

    def test_filter_orders_by_status_with_invalid_status(self):
        url = reverse(self.name_list)
        data = {"status": "NON_EXISTS"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_filter_orders_by_table_number(self):
        url = reverse(self.name_list)
        data = {"table_number": self.order.table_number}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        objects = response.json()["results"]
        self.assertEqual(len(objects), 1)

    def test_filter_orders_by_table_number_for_non_existent(self):
        url = reverse(self.name_list)
        data = {"table_number": "100"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        objects = response.json()["results"]
        self.assertEqual(len(objects), 0)
