from django.urls import path
from . import views

urlpatterns = [
    # ── Existing endpoints ──────────────────────────────────────────── #
    path('english-to-audio/',  views.EnglishToAudioView.as_view(),    name='english_to_audio'),
    path('languages/',         views.SupportedLanguagesView.as_view(), name='supported_languages'),
    path('languages/by-region/', views.LanguagesByRegionView.as_view(), name='languages_by_region'),
    path('history/',           views.AudioHistoryView.as_view(),       name='audio_history'),

    # ── Voice cloning endpoints ─────────────────────────────────────── #
    path('clone-voice/',           views.CloneVoiceView.as_view(),          name='clone_voice'),
    path('generate-cloned-audio/', views.GenerateClonedAudioView.as_view(), name='generate_cloned_audio'),
    path('cloned-voices/',         views.ClonedVoiceListView.as_view(),     name='cloned_voices_list'),
]