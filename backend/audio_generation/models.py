from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AudioFile(models.Model):
   
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name="audio_files")
    original_text = models.TextField()      
    sanitized_text = models.TextField()     
    audio_file = models.FileField(upload_to="audio/%Y/%m/%d/",null=True,blank=True)
    audio_url = models.URLField(max_length=500, blank=True)
    language = models.CharField(max_length=10)  # existing
    target_language = models.CharField(max_length=10, blank=True)
    target_language_name = models.CharField(max_length=50, blank=True)
    tld = models.CharField(max_length=5, default="com")
    slow = models.BooleanField(default=False)
    duration_seconds = models.IntegerField(null=True, blank=True)
    character_count = models.IntegerField()
    word_count = models.IntegerField()
    status = models.CharField(max_length=20, default="pending")
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AudioFile {self.id} - {self.language}"

    VOICE_TYPE_CHOICES = [
        ('female', 'Female'),
        ('male',   'Male'),
    ]

    ENGINE_CHOICES = [
        ('google_cloud_tts', 'Google Cloud TTS'),
        ('gtts_fallback',    'gTTS Fallback'),
        ('xtts_cloned',      'XTTS Cloned Voice'),
        ('',                 'Unknown'),
    ]

    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('processing', 'Processing'),
        ('completed',  'Completed'),
        ('failed',     'Failed'),
    ]

    # ------------------------------------------------------------------ #
    # Core relations & text                                                #
    # ------------------------------------------------------------------ #
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_files')
    original_text   = models.TextField()
    corrected_text  = models.TextField(blank=True, null=True)
    sanitized_text  = models.TextField()

    # ------------------------------------------------------------------ #
    # Audio output                                                         #
    # ------------------------------------------------------------------ #
    audio_file       = models.FileField(upload_to='audio/%Y/%m/%d/', null=True, blank=True)
    audio_url        = models.URLField(max_length=500, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    # ------------------------------------------------------------------ #
    # TTS params                                                           #
    # ------------------------------------------------------------------ #
    language   = models.CharField(max_length=10)
    tld        = models.CharField(max_length=5, default='com')
    slow       = models.BooleanField(default=False)
    voice_type = models.CharField(max_length=10, choices=VOICE_TYPE_CHOICES, default='female')
    engine     = models.CharField(max_length=30, choices=ENGINE_CHOICES, default='', blank=True)

    # ------------------------------------------------------------------ #
    # Voice cloning fields                                                 #
    # ------------------------------------------------------------------ #
    voice_sample_file = models.FileField(
        upload_to='voice_samples/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text='Uploaded voice sample used for cloning',
    )
    cloned_voice_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='UUID referencing the stored speaker embedding',
    )
    is_cloned = models.BooleanField(
        default=False,
        help_text='True when audio was generated using a cloned voice',
    )

    # ------------------------------------------------------------------ #
    # Metrics & status                                                     #
    # ------------------------------------------------------------------ #
    character_count = models.IntegerField()
    word_count      = models.IntegerField()
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message   = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AudioFile #{self.id} — {self.user} — {self.language} — {self.status}"


class ClonedVoice(models.Model):
    """
    Stores metadata about a cloned voice embedding.
    The actual embedding tensor is saved under MEDIA/voice_embeddings/<voice_id>.pt
    """
    voice_id    = models.CharField(max_length=100, unique=True, db_index=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloned_voices')
    name        = models.CharField(max_length=100, blank=True, help_text='Optional user-supplied label')
    sample_file = models.FileField(upload_to='voice_samples/%Y/%m/%d/')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ClonedVoice {self.voice_id} — {self.user}"
