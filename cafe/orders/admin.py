from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Представление связанных записей модели OrderItem"""

    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Представление модели Order в интерфейсе администратора"""

    list_display = (
        "id",
        "status",
        "table_number",
        "created",
        "updated",
        "count_items",
    )
    list_editable = ("status", "table_number")
    list_filter = ("status", "table_number", "created")
    inlines = (OrderItemInline,)

    @admin.display(description="Количество блюд")
    def count_items(self, obj):
        return obj.items.count()
