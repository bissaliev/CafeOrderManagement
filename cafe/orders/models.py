from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Order(models.Model):
    """Модель заказов"""

    class Status(models.TextChoices):
        """Статус заказа"""

        PENDING = "В ожидании"
        READY = "Готово"
        PAID = "Оплачено"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="покупатель",
    )
    table_number = models.CharField(
        "номер стола", max_length=10, db_index=True
    )
    status = models.CharField(
        "статус",
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        max_length=12,
    )
    created = models.DateTimeField("время и дата создания", auto_now_add=True)
    updated = models.DateTimeField("время и дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    """Модель позиций заказа"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="заказ",
    )
    quantity = models.PositiveSmallIntegerField("количество", default=1)
    price = models.DecimalField("стоимость", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
