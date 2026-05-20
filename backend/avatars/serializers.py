from rest_framework import serializers
from .models import Avatar


class AvatarSerializer(serializers.ModelSerializer):

    avatar_image_url = serializers.SerializerMethodField()
    user_image_url = serializers.SerializerMethodField()
    user_video_url = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = "__all__"

    def get_avatar_image_url(self, obj):
        request = self.context.get("request")
        if obj.avatar_image and request:
            return request.build_absolute_uri(obj.avatar_image.url)
        return None

    def get_user_image_url(self, obj):
        request = self.context.get("request")
        if obj.user_image and request:
            return request.build_absolute_uri(obj.user_image.url)
        return None

    def get_user_video_url(self, obj):
        request = self.context.get("request")
        if obj.user_video and request:
            return request.build_absolute_uri(obj.user_video.url)
        return None