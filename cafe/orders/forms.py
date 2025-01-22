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
    # OrderCreate,
    fields=("dish", "quantity"),
    extra=3,
    can_delete=True,
)


class OrderChangeStatus(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)
