from django.urls import path
from orders import views

app_name = "orders"


urlpatterns = [
    path("", views.OrderListView.as_view(), name="order_list"),
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path(
        "<int:id>/update_status/",
        views.OrderChangeStatusView.as_view(),
        name="order_update_status",
    ),
    path(
        "<int:pk>/delete/",
        views.OrderDeleteView.as_view(),
        name="order_delete",
    ),
    path(
        "revenue/",
        views.RevenueView.as_view(),
        name="revenue",
    ),
]
