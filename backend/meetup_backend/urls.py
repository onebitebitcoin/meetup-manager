from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path
from django.views.static import serve


def serve_spa(request, path=''):
    spa_index = Path(settings.BASE_DIR) / 'frontend_dist' / 'index.html'
    if spa_index.exists():
        return FileResponse(open(spa_index, 'rb'), content_type='text/html')
    raise Http404("Frontend not built")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('meetups.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA_FILES:
    urlpatterns += [
        re_path(
            rf"^{settings.MEDIA_URL.lstrip('/')}(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

# Vue SPA catch-all: 모든 비-API 경로에서 index.html 반환 (Vue Router가 클라이언트에서 처리)
urlpatterns += [
    re_path(r'^(?!api/|admin/|static/|media/).*$', serve_spa, name='spa'),
]
