from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from orders.forms import OrderChangeStatus, OrderCreate, OrderItemFormSet
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


class OrderListView(ListView):
    queryset = Order.objects.all()
    template_name = "orders/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"form_status": OrderChangeStatus()})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        table_number = self.request.GET.get("table_number")
        if status:
            queryset = queryset.filter(status=status)
        if table_number:
            queryset = queryset.filter(table_number=table_number)
        return queryset


class OrderChangeStatusView(View):
    def post(self, request, id):
        order = get_object_or_404(Order, pk=id)
        form = OrderChangeStatus(request.POST, instance=order)
        if form.is_valid:
            form.save()
        return redirect("orders:order_list")


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("orders:order_list")
