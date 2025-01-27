from django.core.validators import MinValueValidator
from django.db import models

from orders.utils import calculate_revenue


class Order(models.Model):
    """Модель заказов"""

    class Status(models.TextChoices):
        """Статус заказа"""

        PENDING = "PENDING", "В ожидании"
        READY = "READY", "Готово"
        PAID = "PAID", "Оплачено"

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
    def get_total_revenue_for_periods(cls):
        """
        Получение общей выручки за несколько периодов
        (всё время, сегодня, неделя, месяц).
        """
        queryset = cls.objects.filter(status=cls.Status.PAID)
        return calculate_revenue(queryset)


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
    quantity = models.SmallIntegerField(
        "количество",
        default=1,
        validators=[
            MinValueValidator(1, "Значение должно быть больше или равно 1.")
        ],
    )
    price = models.DecimalField("стоимость", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def save(self, *args, **kwargs):
        """
        Устанавливаем цену позиции, если она не задана. Если уже существует
        позиция с тем же заказом и блюдом, обновляет её количество.
        В противном случае сохраняет текущий объект как новый.
        """
        if not self.price:
            self.price = self.dish.price
        existing_item = OrderItem.objects.filter(
            order=self.order, dish=self.dish
        ).first()

        if existing_item and existing_item.pk != self.pk:
            existing_item.quantity += self.quantity
            existing_item.save()
        else:
            super().save(*args, **kwargs)

    @property
    def total_price(self):
        """Общая стоимости позиции"""
        return self.price * self.quantity
