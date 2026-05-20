"""
services.py — audio_generation

Contains:
  • GTSService        – Google Cloud TTS + gTTS fallback (enhanced)
  • VoiceCloningService – Coqui XTTS v2 voice cloning (singleton, runs inside Django)
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional

from deep_translator import GoogleTranslator
from django.conf import settings

logger = logging.getLogger(__name__)


# =========================================================================== #
#  Helper — speaking-rate / pitch lookup tables                                #
# =========================================================================== #

# (speaking_rate, pitch_semitones)
_MALE_PROFILES = {
    # emotion → base params
    'neutral': (0.87, -5.0),
    'happy':   (0.95, -3.5),
    'serious': (0.82, -6.0),
}
_FEMALE_PROFILES = {
    'neutral': (1.05, 2.0),
    'happy':   (1.12, 4.0),
    'serious': (0.95, 1.0),
}
_SPEED_MULTIPLIERS = {
    'slow':   0.85,
    'normal': 1.00,
    'fast':   1.15,
}


def _voice_params(
    voice_type: str,
    emotion: str = 'neutral',
    speed: str   = 'normal',
) -> tuple[float, float]:
    """Return (speaking_rate, pitch) for Cloud TTS AudioConfig."""
    emotion = emotion if emotion in ('neutral', 'happy', 'serious') else 'neutral'
    speed   = speed   if speed   in ('slow', 'normal', 'fast')      else 'normal'

    profile = (
        _MALE_PROFILES   if voice_type == 'male'
        else _FEMALE_PROFILES
    ).get(emotion, _MALE_PROFILES['neutral'])

    rate  = round(profile[0] * _SPEED_MULTIPLIERS[speed], 3)
    pitch = profile[1]

    # Clamp to Google's documented limits
    rate  = max(0.25, min(4.0, rate))
    pitch = max(-20.0, min(20.0, pitch))
    return rate, pitch


# =========================================================================== #
#  GTSService                                                                  #
# =========================================================================== #

class GTSService:

    # ------------------------------------------------------------------ #
    #  Language / voice maps (unchanged from original)                     #
    # ------------------------------------------------------------------ #

    SUPPORTED_LANGUAGES = {
        # Indian
        'hi': 'Hindi',    'bn': 'Bengali',   'te': 'Telugu',
        'mr': 'Marathi',  'ta': 'Tamil',     'ur': 'Urdu',
        'gu': 'Gujarati', 'kn': 'Kannada',   'ml': 'Malayalam',
        'or': 'Odia',     'pa': 'Punjabi',   'sd': 'Sindhi',
        'ne': 'Nepali',
        # European
        'es': 'Spanish',    'fr': 'French',     'de': 'German',
        'it': 'Italian',    'pt': 'Portuguese', 'ru': 'Russian',
        'tr': 'Turkish',    'nl': 'Dutch',      'pl': 'Polish',
        # Asian
        'ja': 'Japanese', 'ko': 'Korean',  'zh-cn': 'Chinese (Simplified)',
        'vi': 'Vietnamese', 'th': 'Thai',
        # Middle East
        'ar': 'Arabic',
    }

    CLOUD_TTS_VOICE_MAP = {
        'hi':    {'male': 'hi-IN-Wavenet-B',  'female': 'hi-IN-Wavenet-A'},
        'bn':    {'male': 'bn-IN-Wavenet-B',  'female': 'bn-IN-Wavenet-A'},
        'te':    {'male': 'te-IN-Standard-B', 'female': 'te-IN-Standard-A'},
        'mr':    {'male': 'mr-IN-Wavenet-B',  'female': 'mr-IN-Wavenet-A'},
        'ta':    {'male': 'ta-IN-Wavenet-D',  'female': 'ta-IN-Wavenet-A'},
        'ur':    {'male': 'ur-IN-Wavenet-B',  'female': 'ur-IN-Wavenet-A'},
        'gu':    {'male': 'gu-IN-Wavenet-B',  'female': 'gu-IN-Wavenet-A'},
        'kn':    {'male': 'kn-IN-Wavenet-B',  'female': 'kn-IN-Wavenet-A'},
        'ml':    {'male': 'ml-IN-Wavenet-D',  'female': 'ml-IN-Wavenet-A'},
        'or':    {'male': 'or-IN-Standard-B', 'female': 'or-IN-Standard-A'},
        'pa':    {'male': 'pa-IN-Wavenet-B',  'female': 'pa-IN-Wavenet-A'},
        'sd':    {'male': 'ur-IN-Wavenet-B',  'female': 'ur-IN-Wavenet-A'},
        'ne':    {'male': 'ne-NP-Standard-B', 'female': 'ne-NP-Standard-A'},
        'es':    {'male': 'es-ES-Wavenet-B',  'female': 'es-ES-Wavenet-C'},
        'fr':    {'male': 'fr-FR-Wavenet-B',  'female': 'fr-FR-Wavenet-A'},
        'de':    {'male': 'de-DE-Wavenet-B',  'female': 'de-DE-Wavenet-A'},
        'it':    {'male': 'it-IT-Wavenet-C',  'female': 'it-IT-Wavenet-A'},
        'pt':    {'male': 'pt-BR-Wavenet-B',  'female': 'pt-BR-Wavenet-A'},
        'ru':    {'male': 'ru-RU-Wavenet-B',  'female': 'ru-RU-Wavenet-A'},
        'ja':    {'male': 'ja-JP-Wavenet-C',  'female': 'ja-JP-Wavenet-A'},
        'ko':    {'male': 'ko-KR-Wavenet-C',  'female': 'ko-KR-Wavenet-A'},
        'zh-cn': {'male': 'cmn-CN-Wavenet-B', 'female': 'cmn-CN-Wavenet-A'},
        'ar':    {'male': 'ar-XA-Wavenet-B',  'female': 'ar-XA-Wavenet-A'},
        'tr':    {'male': 'tr-TR-Wavenet-B',  'female': 'tr-TR-Wavenet-A'},
        'nl':    {'male': 'nl-NL-Wavenet-B',  'female': 'nl-NL-Wavenet-A'},
        'pl':    {'male': 'pl-PL-Wavenet-B',  'female': 'pl-PL-Wavenet-A'},
        'vi':    {'male': 'vi-VN-Wavenet-B',  'female': 'vi-VN-Wavenet-A'},
        'th':    {'male': 'th-TH-Neural2-C',  'female': 'th-TH-Neural2-A'},
    }

    CLOUD_TTS_LANGUAGE_CODE_MAP = {
        'hi': 'hi-IN', 'bn': 'bn-IN', 'te': 'te-IN', 'mr': 'mr-IN',
        'ta': 'ta-IN', 'ur': 'ur-IN', 'gu': 'gu-IN', 'kn': 'kn-IN',
        'ml': 'ml-IN', 'or': 'or-IN', 'pa': 'pa-IN', 'sd': 'ur-IN',
        'ne': 'ne-NP', 'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE',
        'it': 'it-IT', 'pt': 'pt-BR', 'ru': 'ru-RU', 'ja': 'ja-JP',
        'ko': 'ko-KR', 'zh-cn': 'cmn-CN', 'ar': 'ar-XA', 'tr': 'tr-TR',
        'nl': 'nl-NL', 'pl': 'pl-PL', 'vi': 'vi-VN', 'th': 'th-TH',
    }

    DEFAULT_VOICE_TYPE = 'female'
    _cloud_tts_client  = None   # lazy singleton

    # ------------------------------------------------------------------ #
    #  Cloud TTS client                                                    #
    # ------------------------------------------------------------------ #

    @classmethod
    def _get_cloud_tts_client(cls):
        if cls._cloud_tts_client is None:
            from google.cloud import texttospeech
            cls._cloud_tts_client = texttospeech.TextToSpeechClient()
        return cls._cloud_tts_client

    # ------------------------------------------------------------------ #
    #  Google Cloud TTS (primary)                                          #
    # ------------------------------------------------------------------ #

    @classmethod
    def _generate_audio_cloud_tts(
        cls,
        text:       str,
        lang_short: str,
        voice_type: str,
        emotion:    str = 'neutral',
        speed:      str = 'normal',
    ) -> bytes:
        from google.cloud import texttospeech

        client     = cls._get_cloud_tts_client()
        voice_map  = cls.CLOUD_TTS_VOICE_MAP.get(lang_short, {})
        voice_name = voice_map.get(voice_type) or voice_map.get('female')
        bcp47      = cls.CLOUD_TTS_LANGUAGE_CODE_MAP.get(lang_short, lang_short)

        ssml_gender = (
            texttospeech.SsmlVoiceGender.MALE
            if voice_type == 'male'
            else texttospeech.SsmlVoiceGender.FEMALE
        )

        speaking_rate, pitch = _voice_params(voice_type, emotion, speed)

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params    = texttospeech.VoiceSelectionParams(
            language_code=bcp47,
            name=voice_name,
            ssml_gender=ssml_gender,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config,
        )
        return response.audio_content

    # ------------------------------------------------------------------ #
    #  gTTS fallback                                                       #
    # ------------------------------------------------------------------ #

    @classmethod
    def _generate_audio_gtts_fallback(
        cls,
        text:       str,
        lang_short: str,
        voice_type: str,
        speed:      str = 'normal',
    ) -> bytes:
        from gtts import gTTS

        tld  = 'co.uk' if voice_type == 'male' else 'com'
        slow = (speed == 'slow') or (voice_type == 'male' and speed == 'normal')

        tts = gTTS(text=text, lang=lang_short, tld=tld, slow=slow)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.getvalue()

    # ------------------------------------------------------------------ #
    #  Smart dispatcher                                                    #
    # ------------------------------------------------------------------ #

    @classmethod
    def _generate_audio(
        cls,
        text:       str,
        lang_short: str,
        voice_type: str,
        emotion:    str = 'neutral',
        speed:      str = 'normal',
    ) -> tuple[bytes, str]:
        """Try Cloud TTS; fall back to gTTS.  Returns (audio_bytes, engine_name)."""
        try:
            audio_bytes = cls._generate_audio_cloud_tts(
                text, lang_short, voice_type, emotion, speed
            )
            return audio_bytes, 'google_cloud_tts'
        except Exception as cloud_err:
            logger.warning(
                "Google Cloud TTS unavailable (%s) — falling back to gTTS.", cloud_err
            )
            audio_bytes = cls._generate_audio_gtts_fallback(
                text, lang_short, voice_type, speed
            )
            return audio_bytes, 'gtts_fallback'

    # ------------------------------------------------------------------ #
    #  Text preprocessing                                                  #
    # ------------------------------------------------------------------ #

    @classmethod
    def _preprocess_text_for_voice(
        cls,
        text:       str,
        voice_type: str,
        emotion:    str = 'neutral',
    ) -> str:
        if voice_type == 'male':
            return cls._insert_pauses_for_male(text, aggressive=(emotion == 'serious'))
        # Female / happy — smooth, no extra commas
        return text

    @classmethod
    def _insert_pauses_for_male(cls, text: str, aggressive: bool = False) -> str:
        """
        Insert brief pauses before conjunctions for a measured, authoritative cadence.
        In 'serious' mode also adds pauses around transitional adverbs.
        """
        basic_words = ['and', 'but', 'or', 'so', 'yet', 'because']
        extra_words = ['however', 'therefore', 'furthermore', 'nevertheless', 'moreover']

        words   = basic_words + (extra_words if aggressive else [])
        pattern = r'(?<!\,)\s+\b(' + '|'.join(words) + r')\b'
        text    = re.sub(pattern, r', \1', text, flags=re.IGNORECASE)
        # Collapse any accidental double-commas
        text = re.sub(r',\s*,', ',', text)
        return ' '.join(text.split())

    # ------------------------------------------------------------------ #
    #  Translation                                                         #
    # ------------------------------------------------------------------ #

    @classmethod
    def translate_english_to_target(cls, english_text: str, target_language: str) -> dict:
        try:
            translator   = GoogleTranslator(source='en', target=target_language)
            translated   = translator.translate(english_text)
            return {
                'success':         True,
                'original_text':   english_text,
                'translated_text': translated,
                'target_language': target_language,
            }
        except Exception as e:
            return {'success': False, 'error': f"Translation failed: {e}"}

    # ------------------------------------------------------------------ #
    #  Main entry point                                                    #
    # ------------------------------------------------------------------ #

    @classmethod
    def generate_audio_from_english(
        cls,
        english_text:    str,
        target_language: str,
        tld:             str  = 'com',
        slow:            bool = False,
        voice_type:      str  = 'female',
        emotion:         str  = 'neutral',
        speed:           str  = 'normal',
    ) -> dict:
        """
        Full pipeline: validate → preprocess → translate → synthesise.
        Backward-compatible: callers that omit new params get sensible defaults.
        """
        try:
            if target_language not in cls.SUPPORTED_LANGUAGES:
                return {
                    'success': False,
                    'error': (
                        f"Language '{target_language}' is not supported. "
                        f"Supported: {', '.join(cls.SUPPORTED_LANGUAGES.keys())}"
                    ),
                }

            # Override speed from legacy 'slow' flag when not explicitly set
            effective_speed = 'slow' if (slow and speed == 'normal') else speed

            processed_text = cls._preprocess_text_for_voice(english_text, voice_type, emotion)
            translation    = cls.translate_english_to_target(processed_text, target_language)
            if not translation['success']:
                return {'success': False, 'error': translation['error']}

            audio_bytes, engine_used = cls._generate_audio(
                translation['translated_text'],
                target_language,
                voice_type,
                emotion,
                effective_speed,
            )

            text_hash = hashlib.md5(english_text.encode()).hexdigest()[:10]
            filename  = f"{voice_type}_{target_language}_{text_hash}.mp3"

            return {
                'success':              True,
                'content':              audio_bytes,
                'filename':             filename,
                'original_text':        english_text,
                'translated_text':      translation['translated_text'],
                'target_language':      target_language,
                'target_language_name': cls.SUPPORTED_LANGUAGES[target_language],
                'voice_type':           voice_type,
                'engine':               engine_used,
                'audio_generated':      True,
            }

        except Exception as e:
            logger.exception("generate_audio_from_english failed")
            return {'success': False, 'error': f"Audio generation failed: {e}"}

    # ------------------------------------------------------------------ #
    #  Direct generation (no translation)                                  #
    # ------------------------------------------------------------------ #

    @classmethod
    def generate_audio_direct(
        cls,
        text:       str,
        language:   str,
        tld:        str  = 'com',
        slow:       bool = False,
        voice_type: str  = 'female',
        emotion:    str  = 'neutral',
        speed:      str  = 'normal',
    ) -> dict:
        try:
            if language not in cls.SUPPORTED_LANGUAGES:
                return {'success': False, 'error': f"Language '{language}' is not supported"}

            effective_speed = 'slow' if (slow and speed == 'normal') else speed
            processed_text  = cls._preprocess_text_for_voice(text, voice_type, emotion)
            audio_bytes, engine_used = cls._generate_audio(
                processed_text, language, voice_type, emotion, effective_speed
            )
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            filename  = f"direct_{voice_type}_{language}_{text_hash}.mp3"

            return {
                'success':    True,
                'content':    audio_bytes,
                'filename':   filename,
                'language':   language,
                'voice_type': voice_type,
                'engine':     engine_used,
            }

        except Exception as e:
            logger.exception("generate_audio_direct failed")
            return {'success': False, 'error': str(e)}

    # ------------------------------------------------------------------ #
    #  Utility helpers                                                     #
    # ------------------------------------------------------------------ #

    @classmethod
    def get_supported_languages(cls):
        return cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_supported_voice_types(cls):
        return ['male', 'female']

    @classmethod
    def get_languages_by_region(cls):
        return {
            'Indian Languages': {
                k: v for k, v in cls.SUPPORTED_LANGUAGES.items()
                if k in ['hi', 'bn', 'te', 'mr', 'ta', 'ur', 'gu', 'kn', 'ml', 'or', 'pa', 'sd', 'ne']
            },
            'European Languages': {
                k: v for k, v in cls.SUPPORTED_LANGUAGES.items()
                if k in ['es', 'fr', 'de', 'it', 'pt', 'ru', 'tr', 'nl', 'pl']
            },
            'Asian Languages': {
                k: v for k, v in cls.SUPPORTED_LANGUAGES.items()
                if k in ['ja', 'ko', 'zh-cn', 'vi', 'th']
            },
            'Middle Eastern Languages': {
                k: v for k, v in cls.SUPPORTED_LANGUAGES.items()
                if k in ['ar']
            },
        }


# =========================================================================== #
#  VoiceCloningService — Coqui XTTS v2                                         #
# =========================================================================== #

class VoiceCloningService:
    """
    Singleton-backed voice cloning service using Coqui XTTS v2.

    The TTS model is loaded ONCE at first use and cached at the class level.
    All subsequent requests reuse the warm model — no reloading per request.

    Usage (from views or tasks):
        result = VoiceCloningService.clone_voice(sample_path, voice_id, language)
        result = VoiceCloningService.generate_cloned_audio(text, voice_id, language)
    """

    _model              = None          # xtts model singleton
    _model_lock         = None          # threading.Lock, created lazily
    EMBEDDINGS_DIR_NAME = 'voice_embeddings'

    # ------------------------------------------------------------------ #
    #  Thread-safe lock                                                    #
    # ------------------------------------------------------------------ #

    @classmethod
    def _get_lock(cls):
        if cls._model_lock is None:
            import threading
            cls._model_lock = threading.Lock()
        return cls._model_lock

    # ------------------------------------------------------------------ #
    #  Embeddings directory                                                #
    # ------------------------------------------------------------------ #

    @classmethod
    def _embeddings_dir(cls) -> Path:
        media_root = Path(getattr(settings, 'MEDIA_ROOT', 'media'))
        emb_dir    = media_root / cls.EMBEDDINGS_DIR_NAME
        emb_dir.mkdir(parents=True, exist_ok=True)
        return emb_dir

    @classmethod
    def _embedding_path(cls, voice_id: str) -> Path:
        return cls._embeddings_dir() / f"{voice_id}.pt"

    # ------------------------------------------------------------------ #
    #  Model loading (singleton)                                           #
    # ------------------------------------------------------------------ #

    @classmethod
    def load_model(cls):
        """
        Load XTTS v2 model exactly once.  Thread-safe via double-checked locking.
        Returns the loaded TTS instance.
        """
        if cls._model is not None:
            return cls._model

        with cls._get_lock():
            if cls._model is not None:       # re-check inside the lock
                return cls._model

            try:
                from TTS.api import TTS      # type: ignore[import]

                logger.info("Loading Coqui XTTS v2 model — this may take a minute …")
                tts = TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')
                # Move to GPU if available, otherwise CPU
                try:
                    import torch
                    device      = 'cuda' if torch.cuda.is_available() else 'cpu'
                    cls._model  = tts.to(device)
                    logger.info("XTTS v2 loaded on %s.", device)
                except Exception:
                    cls._model = tts
                    logger.info("XTTS v2 loaded on CPU (torch.cuda check skipped).")

                return cls._model

            except ImportError as ie:
                raise RuntimeError(f"TTS IMPORT ERROR: {str(ie)}") from ie
            except Exception as e:
                logger.exception("REAL ERROR while loading XTTS:")
                raise RuntimeError(f"XTTS REAL ERROR: {str(e)}") from e

    # ------------------------------------------------------------------ #
    #  Clone voice — extract & persist speaker embedding                   #
    # ------------------------------------------------------------------ #

    @classmethod
    def clone_voice(
        cls,
        sample_path: str,
        voice_id:    Optional[str] = None,
        language:    str           = 'en',
    ) -> dict:
        """
        Extract a speaker embedding from an audio sample and save it to disk.

        Parameters
        ----------
        sample_path : str
            Absolute path to the uploaded audio sample (wav / mp3 / etc.).
        voice_id : str | None
            Supply a deterministic ID or leave None to auto-generate a UUID.
        language : str
            BCP-47 language code hint for XTTS (default 'en').

        Returns
        -------
        dict  { 'success': bool, 'voice_id': str } | { 'success': False, 'error': str }
        """
        try:
            import torch  # type: ignore[import]

            if not os.path.isfile(sample_path):
                return {'success': False, 'error': f"Sample file not found: {sample_path}"}

            model    = cls.load_model()
            voice_id = voice_id or str(uuid.uuid4())

            logger.info("Extracting speaker embedding for voice_id=%s …", voice_id)

            # XTTS exposes get_conditioning_latents to extract embeddings
            gpt_cond_latent, speaker_embedding = model.synthesizer.tts_model.get_conditioning_latents(
                audio_path=[sample_path]
            )

            emb_path = cls._embedding_path(voice_id)
            torch.save(
                {
                    'gpt_cond_latent':  gpt_cond_latent.cpu(),
                    'speaker_embedding': speaker_embedding.cpu(),
                    'language':          language,
                },
                str(emb_path),
            )
            logger.info("Speaker embedding saved → %s", emb_path)

            return {'success': True, 'voice_id': voice_id}

        except RuntimeError as e:
            # Propagate model-load errors directly
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.exception("clone_voice failed for sample_path=%s", sample_path)
            return {'success': False, 'error': f"Voice cloning failed: {e}"}

    # ------------------------------------------------------------------ #
    #  Generate audio using a cloned voice                                 #
    # ------------------------------------------------------------------ #

    @classmethod
    def generate_cloned_audio(
        cls,
        text:       str,
        voice_id:   str,
        language:   str = 'en',
    ) -> dict:
        """
        Synthesise speech using a previously cloned voice embedding.

        Returns
        -------
        dict  { 'success': True, 'content': bytes, 'filename': str, 'engine': 'xtts_cloned' }
              | { 'success': False, 'error': str }
        """
        try:
            import torch                       # type: ignore[import]
            import torchaudio                  # type: ignore[import]

            emb_path = cls._embedding_path(voice_id)
            if not emb_path.exists():
                return {
                    'success': False,
                    'error':   f"No embedding found for voice_id '{voice_id}'. "
                               "Please clone the voice first.",
                }

            model   = cls.load_model()
            payload = torch.load(str(emb_path), map_location='cpu')

            gpt_cond_latent  = payload['gpt_cond_latent']
            speaker_embedding = payload['speaker_embedding']
            saved_language   = payload.get('language', language)

            logger.info(
                "Generating cloned audio: voice_id=%s, lang=%s, text_len=%d",
                voice_id, saved_language, len(text),
            )

            # Move embeddings to the model's device
            try:
                device = next(model.synthesizer.tts_model.parameters()).device
                gpt_cond_latent   = gpt_cond_latent.to(device)
                speaker_embedding = speaker_embedding.to(device)
            except Exception:
                pass  # stay on CPU

            # XTTS inference
            out = model.synthesizer.tts_model.inference(
                text=text,
                language=saved_language,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=0.7,
            )

            # Convert waveform → WAV bytes
            wav_tensor = torch.tensor(out['wav']).unsqueeze(0)
            sample_rate = model.synthesizer.output_sample_rate or 24_000

            buf = BytesIO()
            torchaudio.save(buf, wav_tensor, sample_rate, format='wav')
            buf.seek(0)
            audio_bytes = buf.read()

            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            filename  = f"cloned_{voice_id[:8]}_{text_hash}.wav"

            return {
                'success':  True,
                'content':  audio_bytes,
                'filename': filename,
                'engine':   'xtts_cloned',
            }

        except RuntimeError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.exception("generate_cloned_audio failed for voice_id=%s", voice_id)
            return {'success': False, 'error': f"Cloned audio generation failed: {e}"}

    # ------------------------------------------------------------------ #
    #  Utility                                                             #
    # ------------------------------------------------------------------ #

    @classmethod
    def embedding_exists(cls, voice_id: str) -> bool:
        return cls._embedding_path(voice_id).exists()

    @classmethod
    def delete_embedding(cls, voice_id: str) -> bool:
        path = cls._embedding_path(voice_id)
        if path.exists():
            path.unlink()
            return True
        return False