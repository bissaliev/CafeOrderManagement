from django.urls import path

from menu import views

app_name = "menu"

urlpatterns = [
    path("", views.DishListView.as_view(), name="dish_list"),
    path("menu/<int:pk>/", views.DishDetailView.as_view(), name="dish_detail"),
]
