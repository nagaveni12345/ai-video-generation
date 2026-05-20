from text.text_improver import improve_text
from audio_generation.services import GTSService
from audio_generation.models import AudioFile
from django.core.files.base import ContentFile


def process_text_to_audio(user, text, target_language, request=None):

    # -------------------------
    # STEP 1 — Improve Text
    # -------------------------
    improved_text = improve_text(text)

    # -------------------------
    # STEP 2 — Generate Audio
    # -------------------------
    audio_result = GTSService.generate_audio_from_english(
        improved_text,
        target_language
    )

    if not audio_result["success"]:
        return {"success": False, "error": audio_result["error"]}

    # -------------------------
    # STEP 3 — Save Audio Model
    # -------------------------
    audio_instance = AudioFile.objects.create(
        user=user,
        word_count=len(improved_text.split()),
        character_count=len(improved_text),
        target_language=audio_result["target_language"],
        target_language_name=audio_result["target_language_name"],
    )

    # Save file
    audio_instance.audio_file.save(
        audio_result["filename"],
        ContentFile(audio_result["content"]),
        save=True
    )

    # -------------------------
    # STEP 4 — Build Audio URL
    # -------------------------
    if request:
        audio_url = request.build_absolute_uri(audio_instance.file.url)
    else:
        audio_url = audio_instance.audio_file.url

    # -------------------------
    # STEP 5 — Final Response
    # -------------------------
    return {
        "original_text": text,
        "improved_text": improved_text,
        "translated_text": audio_result["translated_text"],

        "audio": {
            "id": audio_instance.id,
            "audio_url": audio_url,
            "duration_seconds": audio_instance.duration_seconds,
            "word_count": audio_instance.word_count,
            "character_count": audio_instance.character_count,
            "target_language": audio_instance.target_language,
            "target_language_name": audio_instance.target_language_name,
            "created_at": audio_instance.created_at,
        },

        "translation_info": {
            "from_language": "English",
            "to_language": audio_result["target_language_name"],
        },

        "success": audio_result.get("success")
    }

    # # STEP 3 — Return response
    # return {
    #     "original_text": text,
    #     "improved_text": improved_text,
    #     "translated_text": audio_result.get("translated_text"),
    #     "audio_filename": audio_result.get("filename"),
    #     "success": audio_result.get("success")
    # }