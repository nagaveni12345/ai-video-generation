from rest_framework import serializers
from .models import AudioFile, ClonedVoice


# --------------------------------------------------------------------------- #
# Request serializers                                                           #
# --------------------------------------------------------------------------- #

class EnglishToAudioSerializer(serializers.Serializer):

    VOICE_TYPE_CHOICES = ['male', 'female']
    EMOTION_CHOICES    = ['neutral', 'happy', 'serious']
    SPEED_CHOICES      = ['slow', 'normal', 'fast']

    text = serializers.CharField(
        min_length=5,
        max_length=2000,
        error_messages={
            'min_length': 'Text must be at least 5 characters long.',
            'max_length': 'Text cannot exceed 2000 characters.',
        },
    )
    target_language = serializers.CharField(max_length=10)
    tld             = serializers.CharField(default='com', required=False)
    slow            = serializers.BooleanField(default=False, required=False)
    voice_type      = serializers.ChoiceField(
        choices=VOICE_TYPE_CHOICES,
        default='female',
        required=False,
    )
    emotion = serializers.ChoiceField(
        choices=EMOTION_CHOICES,
        default='neutral',
        required=False,
    )
    speed = serializers.ChoiceField(
        choices=SPEED_CHOICES,
        default='normal',
        required=False,
    )

    def validate_text(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Text cannot be empty.")
        english_chars = sum(1 for c in stripped if c.isalpha() and ord(c) < 128)
        if len(stripped) > 0 and (english_chars / len(stripped)) < 0.5:
            raise serializers.ValidationError(
                "Text appears not to be English. Please provide English text for translation."
            )
        return stripped

    def validate_target_language(self, value):
        from .services import GTSService
        if value not in GTSService.SUPPORTED_LANGUAGES:
            supported = ', '.join(list(GTSService.SUPPORTED_LANGUAGES.keys())[:20])
            raise serializers.ValidationError(
                f"Language '{value}' not supported. First 20 supported: {supported}"
            )
        return value


class CloneVoiceSerializer(serializers.Serializer):
    voice_sample_file = serializers.FileField()
    name              = serializers.CharField(max_length=100, required=False, default='')

    def validate_voice_sample_file(self, value):
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/ogg', 'audio/flac']
        allowed_exts  = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']

        content_type = getattr(value, 'content_type', '')
        name         = getattr(value, 'name', '').lower()

        ext_ok  = any(name.endswith(e) for e in allowed_exts)
        type_ok = any(ct in content_type for ct in allowed_types) or ext_ok

        if not type_ok:
            raise serializers.ValidationError(
                f"Unsupported file type '{content_type}'. Allowed: wav, mp3, ogg, flac, m4a"
            )

        # 50 MB max
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("Voice sample file must be under 50 MB.")

        # Minimum 3 seconds of audio @ ~16 KB/s ≈ 48 KB
        if value.size < 48_000:
            raise serializers.ValidationError(
                "Voice sample is too short. Please upload at least 3 seconds of clear speech."
            )
        return value


class GenerateClonedAudioSerializer(serializers.Serializer):
    text            = serializers.CharField(min_length=5, max_length=2000)
    cloned_voice_id = serializers.CharField(max_length=100)
    language        = serializers.CharField(max_length=10, default='en', required=False)

    def validate_text(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Text cannot be empty.")
        return stripped


# --------------------------------------------------------------------------- #
# Response serializers                                                          #
# --------------------------------------------------------------------------- #

class AudioResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AudioFile
        fields = [
            'id', 'audio_url', 'duration_seconds', 'word_count',
            'character_count', 'language', 'voice_type', 'engine',
            'is_cloned', 'cloned_voice_id', 'created_at',
        ]


class ClonedVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ClonedVoice
        fields = ['voice_id', 'name', 'created_at']