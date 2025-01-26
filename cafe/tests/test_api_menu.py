from django.urls import reverse
from rest_framework.test import APITestCase

from menu.models import Dish


class TestMenuAPI(APITestCase):
    """Тестирование API Menu"""

    name_list = "api:dishes-list"
    name_detail = "api:dishes-detail"

    @classmethod
    def setUpTestData(cls):
        cls.dish = Dish.objects.create(
            name="dish test", description="testing", price=999
        )

    def test_get_dishes_list(self):
        """Получение списка блюд"""
        url = reverse(self.name_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        objects = response.json()["results"]
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]["id"], self.dish.id)

    def test_get_dish(self):
        """Получение блюда по id"""
        url = reverse(self.name_detail, args=[self.dish.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.dish.id)

    def test_get_non_existent_dish(self):
        """Получение несуществующего блюда"""
        url = reverse(self.name_detail, args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
