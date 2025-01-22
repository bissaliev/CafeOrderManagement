from django.db import models


class Dish(models.Model):
    """Модель блюд"""

    name = models.CharField("Название блюда", max_length=250, unique=True)
    description = models.TextField("Описание блюда")
    price = models.DecimalField(
        "Стоимость блюда", max_digits=10, decimal_places=2
    )
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
