from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Avatar
from .serializers import AvatarSerializer
from .utils import get_age_range
from .services import find_matching_avatar


# ======================================================
# CREATE AVATAR
# ======================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_avatar(request):

    avatar_type = request.data.get("avatar_type")

    # ==================================================
    # OPTION 1 — SELECT FROM ADMIN AVATARS
    # ==================================================
    if avatar_type == "ai":

        gender = request.data.get("gender")
        ethnicity = request.data.get("ethnicity")
        hair_style = request.data.get("hair_style")

        # ✅ SUPPORT AGE SLIDER
        age = request.data.get("age")
        age_range = request.data.get("age_range")

        if age and not age_range:
            age_range = get_age_range(age)

        avatar = find_matching_avatar(
            gender,
            age_range,
            ethnicity,
            hair_style,
        )

        if not avatar:
            return Response(
                {"error": "No matching avatar found"},
                status=404,
            )

        return Response({
            "message": "Matching avatar found",
            "avatar": AvatarSerializer(
                avatar,
                context={"request": request}
            ).data
        })

    # ==================================================
    # OPTION 2 — USER IMAGE UPLOAD
    # ==================================================
    elif avatar_type == "image":

        serializer = AvatarSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            avatar = serializer.save(
                user=request.user,
                status="generated"
            )

            return Response({
                "message": "Image avatar uploaded",
                "avatar": AvatarSerializer(
                    avatar,
                    context={"request": request}
                ).data
            })

        return Response(serializer.errors, status=400)

    # ==================================================
    # OPTION 3 — USER VIDEO UPLOAD
    # ==================================================
    elif avatar_type == "video":

        serializer = AvatarSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            avatar = serializer.save(
                user=request.user,
                status="generated"
            )

            return Response({
                "message": "Video avatar uploaded",
                "avatar": AvatarSerializer(
                    avatar,
                    context={"request": request}
                ).data
            })

        return Response(serializer.errors, status=400)

    return Response({"error": "Invalid avatar type"}, status=400)


# ======================================================
# PREVIEW AVATAR (ADMIN MATCHING IMAGE)
# ======================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def preview_avatar(request):

    gender = request.data.get("gender")
    age = request.data.get("age")
    ethnicity = request.data.get("ethnicity")
    hair_style = request.data.get("hair_style")

    age_range = get_age_range(age)

    avatar = find_matching_avatar(
        gender,
        age_range,
        ethnicity,
        hair_style,
    )

    if not avatar or not avatar.avatar_image:
        return Response(
            {"error": "No matching avatar found"},
            status=404
        )

    return Response({
        "preview_image": request.build_absolute_uri(
            avatar.avatar_image.url
        )
    })


# ======================================================
# ✅ NEW — GET USER AVATARS
# ======================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_avatars(request):

    avatars = Avatar.objects.filter(
        user=request.user
    ).order_by("-created_at")

    serializer = AvatarSerializer(
        avatars,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)


# ======================================================
# ✅ NEW — DELETE AVATAR
# ======================================================
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_avatar(request, avatar_id):

    try:
        avatar = Avatar.objects.get(
            id=avatar_id,
            user=request.user
        )
    except Avatar.DoesNotExist:
        return Response(
            {"error": "Avatar not found"},
            status=404
        )

    avatar.delete()

    return Response({
        "message": "Avatar deleted successfully"
    })