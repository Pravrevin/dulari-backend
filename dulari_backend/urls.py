from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve

from .reset_view import reset_and_load


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/admin/reset-and-load/", reset_and_load, name="reset-and-load"),
    path("api/", include("products.urls")),
    path("api/auth/", include("users.urls")),
    path("api/contact/", include("contact.urls")),
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
