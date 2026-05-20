from __future__ import annotations
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import process_text_to_audio
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import VideoSync
from .serializers import VideoSyncCreateSerializer, VideoSyncListSerializer
from .processor import process_video_sync
import threading


@api_view(["POST"])
def text_to_audio(request):

    text = request.data.get("text")
    target_language = request.data.get("target_language")

    if not text or not target_language:
        return Response(
            {"error": "text and target_language are required"},
            status=400
        )

   
    result = process_text_to_audio(
        user=request.user,
        text=text,
        target_language=target_language
    )

    
    if result.get("audio") and result["audio"].get("audio_url"):
        result["audio"]["audio_url"] = request.build_absolute_uri(
            result["audio"]["audio_url"]
        )

    return Response(result)
class VideoSyncCreateView(generics.CreateAPIView):
    serializer_class   = VideoSyncCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # ✅ Fix: Manually parse booleans from MultiPartParser form data
        hand_gestures      = self.request.data.get('hand_gestures', 'true').lower() != 'false'
        head_movement      = self.request.data.get('head_movement', 'true').lower() != 'false'
        facial_expressions = self.request.data.get('facial_expressions', 'true').lower() != 'false'

        instance = serializer.save(
            user=self.request.user,
            status='pending',
            hand_gestures=hand_gestures,
            head_movement=head_movement,
            facial_expressions=facial_expressions
        )
        # Run processing in background thread
        thread = threading.Thread(target=process_video_sync, args=(instance.id,))
        thread.daemon = True
        thread.start()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # ✅ Fix: Re-serialize saved instance to get correct saved values
        instance = serializer.instance
        output_serializer = self.get_serializer(instance)

        return Response({
            'success': True,
            'message': 'Video submitted for sync. Processing started.',
            'data': output_serializer.data
        }, status=status.HTTP_201_CREATED)


class VideoSyncListView(generics.ListAPIView):
    serializer_class   = VideoSyncListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VideoSync.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset   = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })


class VideoSyncDetailView(generics.RetrieveDestroyAPIView):
    serializer_class   = VideoSyncListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VideoSync.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.video:
            instance.video.delete(save=False)
        if instance.result_video:
            instance.result_video.delete(save=False)
        instance.delete()
        return Response({
            'success': True,
            'message': 'Sync job deleted.'
        }, status=status.HTTP_200_OK)


class VideoSyncStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            job = VideoSync.objects.get(pk=pk, user=request.user)
            return Response({
                'success': True,
                'id': job.id,
                'status': job.status,
                'result_video': request.build_absolute_uri(job.result_video.url) if job.result_video else None,
                'error_message': job.error_message,
            })
        except VideoSync.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sync job not found.'
            }, status=status.HTTP_404_NOT_FOUND)

"""
backend/processing/views.py
============================
Synchronous lipsync video generation endpoint.

POST /api/process/lipsync/
    Runs the full ML pipeline on the same Django server process.
    Waits for completion and returns the final video URL directly.
    No Celery. No polling. No queues.

GET /api/process/lipsync/status/<job_id>/
    Historical job lookup (kept for frontend compatibility).
"""



import logging
import time

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .lipsync_service import run_lipsync_synchronous

logger = logging.getLogger(__name__)


class LipsyncGenerationView(APIView):
    """
    POST /api/process/lipsync/

    Synchronously runs Wav2Lip inference, merges frames, and renders the
    final MP4.  Returns the completed video URL in the response body.

    Request body (JSON):
        {
            "avatar_id": "<AvatarUpload PK or ProcessingJob PK>",
            "audio_id":  "<AudioFile PK>"
        }

    Response 200 OK:
        {
            "success":      true,
            "status":       "completed",
            "video_url":    "/media/generated_videos/<job_id>_lipsync.mp4",
            "video_path":   "/abs/path/to/file.mp4",
            "num_frames":   240,
            "duration_sec": 9.6,
            "elapsed_sec":  38.4
        }

    Response 400 / 404 / 500:
        { "success": false, "error": "<message>" }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        avatar_id = str(request.data.get("avatar_id", "")).strip()
        audio_id  = str(request.data.get("audio_id",  "")).strip()

        # ── Input validation ───────────────────────────────────────────────────
        errors = {}
        if not avatar_id:
            errors["avatar_id"] = "This field is required."
        if not audio_id:
            errors["audio_id"] = "This field is required."
        if errors:
            return Response(
                {"success": False, "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "LipsyncGenerationView.post | user=%s  avatar_id=%s  audio_id=%s",
            request.user.id, avatar_id, audio_id,
        )

        wall_start = time.time()

        result = run_lipsync_synchronous(
            user      = request.user,
            avatar_id = avatar_id,
            audio_id  = audio_id,
        )

        elapsed = round(time.time() - wall_start, 3)

        if not result["success"]:
            error_msg = result.get("error", "Unknown pipeline error.")
            http_code = (
                status.HTTP_404_NOT_FOUND
                if any(
                    kw in error_msg.lower()
                    for kw in ("not found", "not preprocessed", "no face", "missing")
                )
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            logger.error(
                "LipsyncGenerationView: pipeline failed | user=%s  elapsed=%.2fs  error=%s",
                request.user.id, elapsed, error_msg,
            )
            return Response(
                {"success": False, "error": error_msg},
                status=http_code,
            )

        logger.info(
            "LipsyncGenerationView: completed | user=%s  elapsed=%.2fs  video=%s",
            request.user.id, elapsed, result.get("video_url"),
        )

        return Response(
            {
                "success":      True,
                "status":       "completed",
                "video_url":    result["video_url"],
                "video_path":   result["video_path"],
                "num_frames":   result["num_frames"],
                "duration_sec": result["duration_sec"],
                "elapsed_sec":  result["elapsed_sec"],
                "stage_timings": result.get("stage_timings", {}),
                "warnings":     result.get("warnings", []),
            },
            status=status.HTTP_200_OK,
        )


class LipsyncJobStatusView(APIView):
    """
    GET /api/process/lipsync/status/<job_id>/

    Historical lookup — kept for frontend compatibility.
    In the new synchronous architecture this is rarely needed,
    but retained so existing polling clients don't break.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id: str):
        try:
            from .models import LipsyncJob

            job = LipsyncJob.objects.get(job_id=job_id, user=request.user)
        except Exception:
            return Response(
                {"success": False, "error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data: dict = {
            "job_id":     str(job.job_id),
            "status":     job.status,
            "avatar_id":  job.avatar_id,
            "audio_id":   str(job.audio_id),
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }

        if job.status == "completed":
            data["video_url"]    = job.video_url
            data["video_path"]   = job.video_path
            data["num_frames"]   = job.num_frames
            data["duration_sec"] = job.duration_sec
            data["elapsed_sec"]  = job.elapsed_sec
            data["stage_timings"] = job.stage_timings
            data["warnings"]     = job.warnings

        if job.status == "failed":
            data["error_message"] = job.error_message

        return Response({"success": True, "data": data})