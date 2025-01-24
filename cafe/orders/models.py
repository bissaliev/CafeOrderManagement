from datetime import datetime, timedelta

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, F, Sum, When
from django.db.models.functions import Coalesce


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
        Подсчёт общей выручки за несколько периодов
        (всё время, сегодня, неделя, месяц).
        """
        now = datetime.now()
        today = now.date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        # Фильтруем только оплаченные заказы
        queryset = cls.objects.filter(status=cls.Status.PAID)

        # Агрегируем данные
        revenue = queryset.aggregate(
            all_time=Coalesce(
                Sum(F("items__price") * F("items__quantity")),
                0,
                output_field=models.DecimalField(),
            ),
            today=Coalesce(
                Sum(
                    Case(
                        When(
                            updated__date=today,
                            then=F("items__price") * F("items__quantity"),
                        )
                    )
                ),
                0,
                output_field=models.DecimalField(),
            ),
            week=Coalesce(
                Sum(
                    Case(
                        When(
                            updated__date__gte=start_of_week,
                            then=F("items__price") * F("items__quantity"),
                        )
                    )
                ),
                0,
                output_field=models.DecimalField(),
            ),
            month=Coalesce(
                Sum(
                    Case(
                        When(
                            updated__date__gte=start_of_month,
                            then=F("items__price") * F("items__quantity"),
                        )
                    )
                ),
                0,
                output_field=models.DecimalField(),
            ),
        )
        return revenue


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
        if not self.price:
            self.price = self.dish.price
        return super().save(*args, **kwargs)

    @property
    def total_price(self):
        """Общая стоимости позиции"""
        return self.price * self.quantity
