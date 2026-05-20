import os
import uuid
from django.conf import settings
#from TTS.api import TTS
#from moviepy import VideoFileClip, AudioFileClip
from moviepy.editor import VideoFileClip, AudioFileClip


def generate_voiceover(script, output_path):
    """Generate voiceover from script using XTTS"""
    tts = TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')
    tts.tts_to_file(
        text=script,
        language='en',
        file_path=output_path,
        speaker_wav=None,
    )
    return output_path


def merge_audio_with_video(video_path, audio_path, output_path):
    """Merge generated audio with video"""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # If audio is longer than video, trim audio
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    final = video.set_audio(audio)
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')

    video.close()
    audio.close()
    final.close()

    return output_path


def process_video_sync(job_id):
    """Main processing function"""
    from .models import VideoSync

    try:
        job = VideoSync.objects.get(id=job_id)
        job.status = 'processing'
        job.save()

        # Paths
        video_path  = os.path.join(settings.MEDIA_ROOT, job.video.name)
        audio_name  = f"{uuid.uuid4().hex}.wav"
        audio_path  = os.path.join(settings.MEDIA_ROOT, 'processing', 'temp', audio_name)
        result_name = f"{uuid.uuid4().hex}.mp4"
        result_path = os.path.join(settings.MEDIA_ROOT, 'processing', 'results', result_name)

        # Make sure dirs exist
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        os.makedirs(os.path.dirname(result_path), exist_ok=True)

        # Step 1 — Generate voiceover
        generate_voiceover(job.script, audio_path)

        # Step 2 — Merge with video
        merge_audio_with_video(video_path, audio_path, result_path)

        # Step 3 — Save result
        job.result_video = f"processing/results/{result_name}"
        job.status = 'completed'
        job.save()

        # Cleanup temp audio
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        