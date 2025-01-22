from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Sum

User = get_user_model()


class Order(models.Model):
    """Модель заказов"""

    class Status(models.TextChoices):
        """Статус заказа"""

        PENDING = "В ожидании"
        READY = "Готово"
        PAID = "Оплачено"

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
        ordering = ["-created"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order({self.id}) - {self.status}"

    def get_total_price(self):
        """Получение общей суммы заказа"""
        return sum(i.total_price for i in self.items.all())

    @classmethod
    def get_total_revenue(cls):
        return (
            cls.objects.filter(status=cls.Status.PAID)
            .annotate(
                total_order=Sum(F("items__price") * F("items__quantity"))
            )
            .aggregate(total_revenue=Sum("total_order"))["total_revenue"]
        )


class OrderItem(models.Model):
    """Модель позиций заказа"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="заказ",
    )
    dish = models.ForeignKey(
        "menu.Dish", on_delete=models.SET_NULL, null=True, verbose_name="блюдо"
    )
    quantity = models.PositiveSmallIntegerField("количество", default=1)
    price = models.DecimalField("стоимость", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.dish.price
        return super().save(*args, **kwargs)

    @property
    def total_price(self):
        """Общая стоимости позиции"""
        return self.price * self.quantity
