from api.views import menu_views, order_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()
router.register("orders", order_views.OrderViewSet, basename="orders")
router.register("dishes", menu_views.DishReadViewSet, basename="dishes")


urlpatterns = [
    path("", include(router.urls)),
]
