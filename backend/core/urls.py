from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("users.urls", namespace="users")),
    path("api/audio/", include("audio_generation.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/video/", include("video.urls")),
    path("api/avatars/", include("avatars.urls")),

    # unified processing module
    path("api/process/", include("processing.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)