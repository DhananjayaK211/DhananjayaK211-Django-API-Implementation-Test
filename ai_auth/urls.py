from django.contrib import admin
from django.urls import path, include, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import home

schema_view = get_schema_view(
    openapi.Info(
        title="AIEngineer Auth API",
        default_version="v1",
        description="Cookie-auth + CSRF protected APIs with OTP verification",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("authentication.urls")),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", ensure_csrf_cookie(schema_view.without_ui(cache_timeout=0)), name="schema-json"),
    path("swagger/", ensure_csrf_cookie(schema_view.with_ui("swagger", cache_timeout=0)), name="schema-swagger-ui"),
    path("redoc/", ensure_csrf_cookie(schema_view.with_ui("redoc", cache_timeout=0)), name="schema-redoc"),
]
