from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from orders.forms import OrderCreate
from orders.models import Order, OrderItem


class OrderCreateView(LoginRequiredMixin, CreateView):
    queryset = Order
    form_class = OrderCreate
    template_name = "orders/create.html"
    success_url = reverse_lazy("menu:dish_list")

    def form_valid(self, form):
        form = self.get_form()
        order = form.save(commit=False)
        order.user = self.request.user
        order.save()
        dishes = form.cleaned_data.get("items")
        OrderItem.objects.bulk_create(
            [
                OrderItem(order=order, dish=dish, price=dish.price)
                for dish in dishes
            ]
        )
        return super().form_valid(form)
