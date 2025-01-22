from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from orders.forms import OrderCreate, OrderItemFormSet
from orders.models import Order


class OrderCreateView(CreateView):
    queryset = Order.objects.all()
    form_class = OrderCreate
    template_name = "orders/create.html"
    success_url = reverse_lazy("menu:dish_list")

    def form_valid(self, form):
        form = self.get_form()
        order = form.save()
        formset = OrderItemFormSet(self.request.POST, instance=order)
        if formset.is_valid():
            formset.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = OrderItemFormSet()
        context["formset"] = formset
        return context
