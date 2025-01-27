from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from menu.models import Dish
from orders.models import Order, OrderItem


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

        cls.url_order_list = reverse(cls.name_list)
        cls.url_order_detail = reverse(cls.name_detail, args=[cls.order.id])
        cls.url_change_status = reverse(
            cls.name_change_status, args=[cls.order.id]
        )
        cls.url_revenue = reverse(cls.name_revenue)

        cls.new_data = {
            "table_number": "2",
            "items": [
                {
                    "dish": cls.dish.id,
                    "quantity": 1,
                },
            ],
        }

    def test_get_orders_list(self):
        """Получение списка заказов"""
        response = self.client.get(self.url_order_list)
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertIn("results", content)
        self.assertEqual(len(content["results"]), 1)
        self.check_fields(content["results"][0], self.order)

    def test_get_order(self):
        """Получение заказа по id"""
        response = self.client.get(self.url_order_detail)
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.check_fields(content, self.order)

    def check_fields(self, req_obj, db_obj):
        fields = ("id", "table_number", "status")
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, req_obj)
                self.assertEqual(req_obj[field], getattr(db_obj, field))
                self.assertIn("items", req_obj)
        self.assertEqual(
            Decimal(req_obj["total_price"]),
            sum(i.price * i.quantity for i in db_obj.items.all()),
        )

    def test_get_non_existent_order(self):
        """Получение несуществующего заказа возвращает ошибку 404"""
        url = reverse(self.name_detail, args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_order_is_correct(self):
        """Создание заказа выполняется корректно с валидными данными"""
        response = self.client.post(
            self.url_order_list, data=self.new_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        new_order = Order.objects.filter(
            table_number=self.new_data["table_number"],
            items__dish_id=self.new_data["items"][0]["dish"],
        ).first()
        self.assertTrue(new_order)

    def test_create_order_dishes_saved_as_one_item(self):
        """
        Создание заказа при указании одинаковых блюд сохраняет блюда в одну
        позицию с суммированием количества
        """
        self.new_data["items"].append(self.new_data["items"][0])
        response = self.client.post(
            self.url_order_list, data=self.new_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        order = Order.objects.filter(
            table_number=self.new_data["table_number"]
        ).first()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)

    def test_create_order_with_invalid_data(self):
        """Создание заказа с невалидными данными"""
        invalid_data = (
            {"status": "NOT STATUS"},
            {"items": [{"dish": self.dish.id, "quantity": 0}]},
            {"items": [{"dish": 100, "quantity": 1}]},
        )

        for data in invalid_data:
            field, value = list(data.keys())[0], list(data.values())[0]
            with self.subTest(field=field):
                self.new_data[field] = value
                response = self.client.post(
                    self.url_order_list, data=self.new_data, format="json"
                )
                self.assertEqual(response.status_code, 400)

    def test_update_order_is_correct(self):
        """Корректно изменяются данные заказа"""
        new_dish = Dish.objects.create(
            name="dish test 2", description="testing", price=100
        )
        self.new_data["items"][0]["dish"] = new_dish.id
        response = self.client.patch(
            self.url_order_detail, data=self.new_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.table_number, self.new_data["table_number"]
        )
        self.assertEqual(self.order.items.count(), 1)

    def test_update_order_is_correct_quantity(self):
        """
        Изменение заказа при указании одинаковых блюд сохраняет блюда в одну
        позицию с суммирование количества
        """
        new_quantity = 5
        new_items = []
        for _ in range(1, 3):
            new_items.append({"dish": self.dish.id, "quantity": new_quantity})
        self.new_data["items"] = new_items
        response = self.client.patch(
            self.url_order_detail, data=self.new_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.table_number, self.new_data["table_number"]
        )
        self.assertEqual(self.order.items.count(), 1)
        order_item = OrderItem.objects.filter(order=self.order).first()
        self.assertEqual(order_item.quantity, new_quantity * 2)

    def test_change_status_orders(self):
        """Изменение статуса выполняется корректно"""
        statuses = ["NON STATUS"] + Order.Status.values
        expected = [self.order.status] + Order.Status.values
        status_codes = (400, 201, 201, 201)
        for st, exp, status_code in zip(statuses, expected, status_codes):
            with self.subTest(status=st):
                response = self.client.patch(
                    self.url_change_status,
                    data={"status": st},
                    format="json",
                )
                self.assertEqual(response.status_code, status_code)
                self.order.refresh_from_db()
                self.assertEqual(self.order.status, exp)

    def test_get_revenue(self):
        """Корректно возвращается расчет выручки"""
        for status in Order.Status:
            self.order.status = status
            self.order.save()
            response = self.client.get(self.url_revenue)
            self.assertEqual(response.status_code, 200)
            revenue = response.json()
            revenue_from_db = Order.get_total_revenue_for_periods()
            for key, value in revenue.items():
                with self.subTest(key=key, status=status.value):
                    self.assertEqual(Decimal(value), revenue_from_db[key])

    def test_filter_orders_is_correct(self):
        """Заказы корректно фильтруются по номеру стола и статусу"""
        filtering_data = (
            ("status", self.order.status, 1),
            ("table_number", "100", 0),
            ("table_number", self.order.table_number, 1),
        )
        for field, value, expected_count in filtering_data:
            with self.subTest(field=field):
                response = self.client.get(
                    self.url_order_list, data={field: value}
                )
                self.assertEqual(response.status_code, 200)
                objects = response.json()["results"]
                self.assertEqual(len(objects), expected_count)

    def test_filter_orders_by_status_with_invalid_status(self):
        """
        Запрос при фильтрации по несуществующему статусу возвращает ошибку 400
        """
        data = {"status": "NON_EXISTS"}
        response = self.client.get(self.url_order_list, data=data)
        self.assertEqual(response.status_code, 400)
