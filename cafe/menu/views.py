from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from menu.models import Dish


class DishListView(ListView):
    template_name = "menu/list.html"
    queryset = Dish.objects.all()
    paginate_by = 12


class DishDetailView(DetailView):
    queryset = Dish.objects.all()
    template_name = "menu/detail.html"
