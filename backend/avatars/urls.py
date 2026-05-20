
from django.urls import path
from .views import create_avatar, preview_avatar, my_avatars, delete_avatar


urlpatterns = [
    path("create-avatar/", create_avatar, name="create-avatar"),
    path("preview/", preview_avatar),
    path("my/", my_avatars),
    path("delete/<int:avatar_id>/", delete_avatar)
]