from django import forms
from menu.models import Dish
from orders.models import Order

TABLE_CHOSES = [(i, str(i)) for i in range(1, 11)]


class OrderCreate(forms.ModelForm):
    table_number = forms.ChoiceField(
        choices=TABLE_CHOSES,
        label="Номер столика",
        help_text="Выберите столик",
    )
    items = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.all(), label="Блюда"
    )

    class Meta:
        model = Order
        fields = ("table_number",)
