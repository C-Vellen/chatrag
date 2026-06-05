from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^user/", include("user.urls", namespace="user")),
    re_path(r"^ingest/", include("ingest.urls", namespace="ingest")),
    re_path(r"^retrieval/", include("retrieval.urls", namespace="retrieval")),
    re_path(r"^chat/", include("chat.urls", namespace="chat")),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(
        r"^", include("home.urls", namespace="home")
    ),  # positionner toujours en dernier !
]

if settings.HAS_SPECIAL_APP:
    urlpatterns += [
        re_path(r"^special/", include("special.urls", namespace="special")),
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
