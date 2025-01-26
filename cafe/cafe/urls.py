from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("menu.urls", namespace="menu")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("api/v1/", include("api.urls", namespace="api")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
