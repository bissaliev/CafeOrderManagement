from django.contrib import admin
from menu.models import Dish


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    """Блюда"""

    list_display = ("id", "name", "price", "is_active")
    list_editable = ("price", "is_active")
    list_filter = ("price", "is_active")
