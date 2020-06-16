from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/post/", include("post.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    schema_view = get_schema_view(
        openapi.Info(
            title="Sample API",
            default_version="v1",
            description="Test description",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        validators=["flex"],
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        re_path(
            r"^v1/swagger(?P<format>\.json|\.yaml)/$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^v1/swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        re_path(
            r"^v1/redoc/$",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc-v1",
        ),
    ]
