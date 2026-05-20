from rest_framework import serializers
from .models import VideoSync

hand_gestures      = serializers.BooleanField(default=True)
head_movement      = serializers.BooleanField(default=True)
facial_expressions = serializers.BooleanField(default=True) 

class VideoSyncCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VideoSync
        fields = [
            'id', 'video', 'script',
            'hand_gestures', 'head_movement', 'facial_expressions',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']
        extra_kwargs = {
            'video': {'max_length': None}  # remove filename length limit
        }

    def validate_video(self, value):
        allowed_types = ['video/mp4', 'video/webm', 'video/quicktime']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only MP4, WEBM, and MOV videos are allowed.")
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("Video size must be under 100MB.")
        return value

    def validate_script(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Script must be at least 5 characters.")
        return value


class VideoSyncListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VideoSync
        fields = [
            'id', 'video', 'script',
            'hand_gestures', 'head_movement', 'facial_expressions',
            'status', 'result_video', 'error_message', 'created_at'
        ]
        extra_kwargs = {
            'video': {'max_length': None}
        }
        