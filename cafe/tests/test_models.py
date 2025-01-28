from django.test import TestCase

from menu.models import Dish
from orders.models import Order, OrderItem


class TestOrderModel(TestCase):
    """Тестирование моделей Order & OrderItem"""

    periods = ("all_time", "month", "week", "today")

    @classmethod
    def setUpTestData(cls):
        cls.dishes = Dish.objects.bulk_create(
            [Dish(name=f"dish_{i}", price=i * 100) for i in range(1, 3)]
        )
        cls.order = Order.objects.create(table_number="1")
        OrderItem.objects.bulk_create(
            [
                OrderItem(order=cls.order, dish=i, price=i.price)
                for i in cls.dishes
            ]
        )

    def test_of_saving_orders_without_specifying_price(self):
        """Метод save корректно сохраняет стоимость в заказе"""
        dish = self.dishes[0]
        order = Order.objects.create(table_number="1")
        orderitem = OrderItem.objects.create(
            order=order, dish=dish, quantity=1
        )
        self.assertEqual(dish.price, orderitem.price)

    def test_calculation_revenue_also_status_is_paid(self):
        """
        Проверка корректности вычисления выручки.
        При отсутствии оплаченных заказов возвращается ноль
        """
        expected = 0
        revenue = Order.get_total_revenue_for_periods()
        for period in self.periods:
            with self.subTest(period=period):
                self.assertIn(period, revenue)
                self.assertEqual(revenue[period], expected)

    def test_calculation_revenue_is_correct(self):
        """
        Проверка корректности вычисления выручки для оплаченных заказов
        """
        self.order.status = Order.Status.PAID
        self.order.save()
        expected = sum(i.price * i.quantity for i in self.order.items.all())
        revenue = Order.get_total_revenue_for_periods()
        for period in self.periods:
            with self.subTest(period=period):
                self.assertIn(period, revenue)
                self.assertEqual(revenue[period], expected)
