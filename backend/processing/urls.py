from django.urls import path
from .views import (
    text_to_audio,
    VideoSyncCreateView,
    VideoSyncListView,
    VideoSyncDetailView,
    VideoSyncStatusView,
    LipsyncGenerationView,
    LipsyncJobStatusView,
)

app_name = "processing"

urlpatterns = [
    # Text to Audio
    path("text-to-audio/", text_to_audio, name="text_to_audio"),

    # Existing Video Sync APIs
    path("sync/", VideoSyncCreateView.as_view(), name="video-sync-create"),
    path("sync/list/", VideoSyncListView.as_view(), name="video-sync-list"),
    path("sync/<int:pk>/", VideoSyncDetailView.as_view(), name="video-sync-detail"),
    path("sync/<int:pk>/status/", VideoSyncStatusView.as_view(), name="video-sync-status"),

    # New Lipsync APIs
    path("lipsync/", LipsyncGenerationView.as_view(), name="lipsync-generate"),
    path("lipsync/status/<str:job_id>/", LipsyncJobStatusView.as_view(), name="lipsync-status"),
]