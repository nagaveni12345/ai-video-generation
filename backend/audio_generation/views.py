"""
views.py — audio_generation

All views run inside the same Django server; no external ML service is contacted.
"""

import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from .models import AudioFile, ClonedVoice
from .serializers import (
    AudioResponseSerializer,
    ClonedVoiceSerializer,
    CloneVoiceSerializer,
    EnglishToAudioSerializer,
    GenerateClonedAudioSerializer,
)
from .services import GTSService, VoiceCloningService
from .utils import improve_text_with_groq, validate_and_process_text

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Rate throttle                                                                 #
# --------------------------------------------------------------------------- #

class AudioRateThrottle(UserRateThrottle):
    rate = '30/hour'


# --------------------------------------------------------------------------- #
# 1. English → translated audio                                                 #
# --------------------------------------------------------------------------- #

class EnglishToAudioView(APIView):
    """
    POST /api/audio/english-to-audio/

    Accepts English text, optionally corrects it via Groq, translates it
    to the target language, then synthesises speech using Google Cloud TTS
    (with automatic gTTS fallback).
    """

    permission_classes = [IsAuthenticated]
    throttle_classes   = [AudioRateThrottle]

    def post(self, request):

        # ---------------------------------------------------------------- #
        # 1. Validate request body                                          #
        # ---------------------------------------------------------------- #
        serializer = EnglishToAudioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data            = serializer.validated_data
        original_text   = data['text']
        target_language = data['target_language']
        tld             = data.get('tld', 'com')
        slow            = data.get('slow', False)
        voice_type      = data.get('voice_type', 'female')
        emotion         = data.get('emotion', 'neutral')
        speed           = data.get('speed', 'normal')

        # ---------------------------------------------------------------- #
        # 2. Optional text correction via Groq                              #
        # ---------------------------------------------------------------- #
        corrected_text          = original_text
        text_correction_applied = False

        try:
            improved = improve_text_with_groq(original_text)
            if improved and improved != original_text:
                corrected_text          = improved
                text_correction_applied = True
        except Exception as exc:
            logger.warning("Groq text correction skipped: %s", exc)

        # ---------------------------------------------------------------- #
        # 3. Validate & sanitize                                            #
        # ---------------------------------------------------------------- #
        try:
            validation    = validate_and_process_text(corrected_text)
            final_text    = validation['sanitized_text']
            text_analysis = validation['analysis']
        except ValueError as exc:
            return Response(
                {'success': False, 'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------------- #
        # 4. Persist initial DB record                                      #
        # ---------------------------------------------------------------- #
        audio_record = AudioFile.objects.create(
            user            = request.user,
            original_text   = original_text,
            corrected_text  = corrected_text if text_correction_applied else None,
            sanitized_text  = final_text,
            character_count = text_analysis['character_count'],
            word_count      = text_analysis['word_count'],
            language        = target_language,
            tld             = tld,
            slow            = slow,
            voice_type      = voice_type,
            status          = 'processing',
        )

        # ---------------------------------------------------------------- #
        # 5. Generate audio (Cloud TTS → gTTS fallback)                    #
        # ---------------------------------------------------------------- #
        result = GTSService.generate_audio_from_english(
            english_text    = final_text,
            target_language = target_language,
            tld             = tld,
            slow            = slow,
            voice_type      = voice_type,
            emotion         = emotion,
            speed           = speed,
        )

        if not result['success']:
            audio_record.status        = 'failed'
            audio_record.error_message = result.get('error', 'Unknown error')
            audio_record.save()
            return Response(
                {'success': False, 'error': result.get('error', 'Audio generation failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ---------------------------------------------------------------- #
        # 6. Persist audio file and update record                           #
        # ---------------------------------------------------------------- #
        file_path = default_storage.save(
            f"audio/{request.user.id}/{result['filename']}",
            ContentFile(result['content']),
        )

        audio_record.sanitized_text  = result['translated_text']
        audio_record.audio_file      = file_path
        audio_record.audio_url       = request.build_absolute_uri(
            settings.MEDIA_URL + file_path
        )
        audio_record.status          = 'completed'
        audio_record.engine          = result.get('engine', '')
        if 'duration_seconds' in result:
            audio_record.duration_seconds = result['duration_seconds']
        audio_record.save()

        # ---------------------------------------------------------------- #
        # 7. Build and return response                                      #
        # ---------------------------------------------------------------- #
        return Response(
            {
                'success': True,
                'data': {
                    'id':                   audio_record.id,
                    'audio_url':            audio_record.audio_url,
                    'duration_seconds':     audio_record.duration_seconds,
                    'word_count':           audio_record.word_count,
                    'character_count':      audio_record.character_count,
                    'target_language':      target_language,
                    'target_language_name': result['target_language_name'],
                    'voice_type':           voice_type,
                    'engine':               result.get('engine', ''),
                    'created_at':           audio_record.created_at,
                },
                'translation_info': {
                    'original_text':   original_text,
                    'corrected_text':  corrected_text if text_correction_applied else None,
                    'text_corrected':  text_correction_applied,
                    'translated_text': result['translated_text'],
                    'from_language':   'English',
                    'to_language':     result['target_language_name'],
                },
            },
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------------- #
# 2. Supported languages                                                        #
# --------------------------------------------------------------------------- #

class SupportedLanguagesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'success': True,
            'data':    GTSService.get_supported_languages(),
        })


# --------------------------------------------------------------------------- #
# 3. Languages by region                                                        #
# --------------------------------------------------------------------------- #

class LanguagesByRegionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'success': True,
            'data':    GTSService.get_languages_by_region(),
        })


# --------------------------------------------------------------------------- #
# 4. Audio history                                                              #
# --------------------------------------------------------------------------- #

class AudioHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page  = max(1, int(request.GET.get('page',  1)))
            limit = max(1, min(100, int(request.GET.get('limit', 10))))
        except (TypeError, ValueError):
            page, limit = 1, 10

        offset = (page - 1) * limit
        qs     = AudioFile.objects.filter(user=request.user, status='completed')

        total     = qs.count()
        audios    = qs.order_by('-created_at')[offset:offset + limit]
        serializer = AudioResponseSerializer(audios, many=True)

        return Response({
            'success': True,
            'data': {
                'audios':     serializer.data,
                'pagination': {
                    'page':  page,
                    'limit': limit,
                    'total': total,
                    'pages': max(1, (total + limit - 1) // limit),
                },
            },
        })


# --------------------------------------------------------------------------- #
# 5. Clone voice                                                                #
# --------------------------------------------------------------------------- #

class CloneVoiceView(APIView):
    """
    POST /api/audio/clone-voice/

    Upload an audio sample (wav/mp3/ogg/flac) to extract a speaker embedding.
    Returns a cloned_voice_id that can be passed to GenerateClonedAudioView.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes   = [AudioRateThrottle]

    def post(self, request):
        serializer = CloneVoiceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = serializer.validated_data['voice_sample_file']
        name          = serializer.validated_data.get('name', '')

        # Persist the sample file under MEDIA/voice_samples/
        file_path = default_storage.save(
            f"voice_samples/{request.user.id}/{uploaded_file.name}",
            ContentFile(uploaded_file.read()),
        )
        abs_sample_path = default_storage.path(file_path)

        # Generate a unique voice_id
        import uuid
        voice_id = str(uuid.uuid4())

        # Extract and persist the speaker embedding (runs inside this server)
        result = VoiceCloningService.clone_voice(
            sample_path = abs_sample_path,
            voice_id    = voice_id,
        )

        if not result['success']:
            # Clean up uploaded file on failure
            try:
                default_storage.delete(file_path)
            except Exception:
                pass
            return Response(
                {'success': False, 'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Persist metadata in DB
        cloned_voice = ClonedVoice.objects.create(
            voice_id    = voice_id,
            user        = request.user,
            name        = name,
            sample_file = file_path,
        )

        return Response(
            {
                'success': True,
                'data': ClonedVoiceSerializer(cloned_voice).data,
            },
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------------- #
# 6. Generate cloned audio                                                      #
# --------------------------------------------------------------------------- #

class GenerateClonedAudioView(APIView):
    """
    POST /api/audio/generate-cloned-audio/

    Synthesise speech using a previously cloned voice embedding.
    The cloned_voice_id must belong to the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes   = [AudioRateThrottle]

    def post(self, request):
        serializer = GenerateClonedAudioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data            = serializer.validated_data
        text            = data['text']
        cloned_voice_id = data['cloned_voice_id']
        language        = data.get('language', 'en')

        # Verify ownership
        try:
            ClonedVoice.objects.get(voice_id=cloned_voice_id, user=request.user)
        except ClonedVoice.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error':   "Voice ID not found or does not belong to this account.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate & sanitize text
        try:
            validation    = validate_and_process_text(text)
            final_text    = validation['sanitized_text']
            text_analysis = validation['analysis']
        except ValueError as exc:
            return Response(
                {'success': False, 'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create initial DB record
        audio_record = AudioFile.objects.create(
            user            = request.user,
            original_text   = text,
            sanitized_text  = final_text,
            character_count = text_analysis['character_count'],
            word_count      = text_analysis['word_count'],
            language        = language,
            voice_type      = 'female',   # N/A for cloned; stored as default
            cloned_voice_id = cloned_voice_id,
            is_cloned       = True,
            status          = 'processing',
        )

        # Generate audio using XTTS cloned voice (runs inside this server)
        result = VoiceCloningService.generate_cloned_audio(
            text     = final_text,
            voice_id = cloned_voice_id,
            language = language,
        )

        if not result['success']:
            audio_record.status        = 'failed'
            audio_record.error_message = result.get('error', 'Unknown error')
            audio_record.save()
            return Response(
                {'success': False, 'error': result.get('error', 'Audio generation failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Persist audio file
        file_path = default_storage.save(
            f"audio/{request.user.id}/{result['filename']}",
            ContentFile(result['content']),
        )

        audio_record.audio_file  = file_path
        audio_record.audio_url   = request.build_absolute_uri(
            settings.MEDIA_URL + file_path
        )
        audio_record.status      = 'completed'
        audio_record.engine      = 'xtts_cloned'
        audio_record.save()

        return Response(
            {
                'success': True,
                'data': {
                    'id':               audio_record.id,
                    'audio_url':        audio_record.audio_url,
                    'cloned_voice_id':  cloned_voice_id,
                    'word_count':       audio_record.word_count,
                    'character_count':  audio_record.character_count,
                    'language':         language,
                    'engine':           'xtts_cloned',
                    'created_at':       audio_record.created_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------------- #
# 7. List cloned voices                                                         #
# --------------------------------------------------------------------------- #

class ClonedVoiceListView(APIView):
    """
    GET /api/audio/cloned-voices/
    List all cloned voice embeddings belonging to the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        voices     = ClonedVoice.objects.filter(user=request.user).order_by('-created_at')
        serializer = ClonedVoiceSerializer(voices, many=True)
        return Response({'success': True, 'data': serializer.data})