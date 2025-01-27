from django import forms
from django.forms import inlineformset_factory

from menu.models import Dish
from orders.models import Order, OrderItem

TABLE_CHOSES = [(i, str(i)) for i in range(1, 11)]


class OrderForm(forms.ModelForm):
    """Форма создания заказа"""

    table_number = forms.ChoiceField(
        choices=TABLE_CHOSES,
        label="Номер столика",
        help_text="Выберите столик",
    )

    class Meta:
        model = Order
        fields = ("table_number",)


class OrderItemForm(forms.ModelForm):
    """Форма позиций заказа"""

    class Meta:
        model = OrderItem
        fields = ("dish", "quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dish"].queryset = Dish.objects.filter(is_active=True)


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    OrderItemForm,
    fields=("dish", "quantity"),
    extra=4,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class OrderFormChangeStatus(forms.ModelForm):
    """Форма обновления статуса заказа"""

    class Meta:
        model = Order
        fields = ("status",)
