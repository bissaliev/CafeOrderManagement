from django.test import TestCase
from django.urls import reverse

from menu.models import Dish


class TestMenuContent(TestCase):
    """Тестирование контента приложения menu"""

    url_name_list = "menu:dish_list"
    url_name_detail = "menu:dish_detail"

    @classmethod
    def setUpTestData(cls):
        cls.dish = Dish.objects.create(
            name="test dish",
            description="test-dish",
            price=999,
        )

    def test_menu_list_render_is_correct(self):
        """Проверка отображения списка блюд"""
        url = reverse(self.url_name_list)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertEqual(object_list[0].id, self.dish.id)
        self.assertEqual(len(object_list), 1)

    def test_menu_detail_render_is_correct(self):
        """Проверка отображения подробного описания блюда"""
        url = reverse(self.url_name_detail, args=[self.dish.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("object", response.context)
        object = response.context["object"]
        self.assertEqual(object.id, self.dish.id)


class TestMenuPaginator(TestCase):
    """Тестирование пагинации на странице списка блюд"""

    url_list = reverse("menu:dish_list")
    pages_count = 12

    @classmethod
    def setUpTestData(cls):
        cls.expected_count = (cls.pages_count, 1)
        cls.dishes = Dish.objects.bulk_create(
            [
                Dish(
                    name=f"dish-{i}",
                    description=f"test-dish-{i}",
                    price=100,
                )
                for i in range(sum(cls.expected_count))
            ]
        )

    def test_menu_list_render_is_correct(self):
        """Тестирование пагинации на странице списка блюд"""
        for page, count in enumerate(self.expected_count, 1):
            url = f"{self.url_list}?page={page}"
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn("object_list", response.context)
                object_list = response.context["object_list"]
                self.assertEqual(len(object_list), count)
