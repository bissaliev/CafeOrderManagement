from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from orders.forms import OrderChangeStatus, OrderCreate, OrderItemFormSet
from orders.models import Order


class OrderCreateUpdateBaseView:
    """Базовый класс для добавления форм обработки позиций заказа"""

    queryset = Order.objects.all()
    form_class = OrderCreate
    template_name = "orders/create.html"
    success_url = reverse_lazy("orders:order_list")
    formset_class = OrderItemFormSet

    def form_valid(self, form):
        """Добавить обработку formset для позиций заказа"""
        order = form.save(commit=False)
        formset = self.formset_class(self.request.POST, instance=order)
        if formset.is_valid():
            formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            order.save()
            formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавить formset для позиций заказа в контекст"""
        context = super().get_context_data(**kwargs)
        context["formset"] = self.formset_class(
            self.request.POST or None, instance=self.get_instance()
        )
        return context

    def get_instance(self):
        return NotImplementedError(
            "Метод get_instance() должен быть реализован в наследниках."
        )


class OrderCreateView(OrderCreateUpdateBaseView, CreateView):
    """Создание заказа"""

    def get_instance(self):
        return None


class OrderUpdateView(OrderCreateUpdateBaseView, UpdateView):
    """Редактирование заказа"""

    def get_instance(self):
        return self.get_object()


class OrderListView(ListView):
    """Список заказов"""

    queryset = Order.objects.prefetch_related("items", "items__dish")
    template_name = "orders/list.html"
    paginate_by = 20

    def get_queryset(self):
        """
        Добавить обработку фильтрации по статусу и поиск по номеру столика
        """
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        table_number = self.request.GET.get("table_number")
        if status:
            queryset = queryset.filter(status=status)
        if table_number:
            queryset = queryset.filter(table_number=table_number)
        return queryset


class OrderChangeStatusView(View):
    """Изменить статус заказа"""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderChangeStatus(request.POST, instance=order)
        if form.is_valid:
            form.save()
        return redirect("orders:order_list")


class OrderDeleteView(DeleteView):
    """Удаление заказа"""

    model = Order
    success_url = reverse_lazy("orders:order_list")


class RevenueView(TemplateView):
    """Вывод выручки за периоды: все время, месяц, неделю, сегодня"""

    template_name = "orders/revenue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        revenue_period = Order.get_total_revenue_for_periods()
        context["revenue_period"] = revenue_period
        return context
