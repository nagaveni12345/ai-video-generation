"""
backend/video/urls.py
URL routing for the video / avatar / dashboard module.

Mount in backend/core/urls.py with:

    path("api/video/", include("backend.video.urls")),
"""

from django.urls import path

from .views import (
    # Avatar preprocessing
    ProcessAvatarView,
    ProcessingJobStatusView,
    # Dashboard
    DashboardView,
    CreateProjectView,
    DeleteProjectView,
    ProjectStatsView,
    # Video generation (function-based)
    generate_video,
    get_job_status,
    list_jobs,
    cancel_job,
)

app_name = "video"

urlpatterns = [
    # ── Avatar preprocessing ──────────────────────────────────────────────────
    # POST  → upload file + trigger preprocessing
    path("process-avatar/",          ProcessAvatarView.as_view(),       name="process_avatar"),
    # GET   → poll preprocessing job status
    path("process-avatar/<str:job_id>/", ProcessingJobStatusView.as_view(), name="job_status"),

    # ── Video generation jobs ─────────────────────────────────────────────────
    # POST  → trigger video generation
    path("generate/",                generate_video,                    name="generate_video"),
    # GET   → list all jobs for the authenticated user
    path("jobs/",                    list_jobs,                         name="list_jobs"),
    # GET   → get status of a specific job
    path("jobs/<uuid:job_id>/",      get_job_status,                    name="get_job_status"),
    # POST  → cancel a job
    path("jobs/<uuid:job_id>/cancel/", cancel_job,                      name="cancel_job"),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    # GET   → stats + recent projects
    path("dashboard/",               DashboardView.as_view(),           name="dashboard"),
    # GET   → stats only
    path("dashboard/stats/",         ProjectStatsView.as_view(),        name="dashboard_stats"),
    # POST  → create project
    path("dashboard/projects/",      CreateProjectView.as_view(),       name="create_project"),
    # DELETE → delete project
    path("dashboard/projects/<str:project_id>/", DeleteProjectView.as_view(), name="delete_project"),
]