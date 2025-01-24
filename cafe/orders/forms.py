from django import forms
from django.forms import inlineformset_factory
from orders.models import Order, OrderItem

TABLE_CHOSES = [(i, str(i)) for i in range(1, 11)]


class OrderCreate(forms.ModelForm):
    table_number = forms.ChoiceField(
        choices=TABLE_CHOSES,
        label="Номер столика",
        help_text="Выберите столик",
    )

    class Meta:
        model = Order
        fields = ("table_number",)


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=("dish", "quantity"),
    extra=4,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class OrderChangeStatus(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)
