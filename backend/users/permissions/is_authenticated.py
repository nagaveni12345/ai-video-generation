"""
users/permissions/is_authenticated.py

Custom permission class for VidAI Studio.
Extends DRF's IsAuthenticated with deactivated-account protection.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAuthenticatedUser(IsAuthenticated):
    """
    Grants access only to active, authenticated users.

    Extends DRF's IsAuthenticated to:
    - Explicitly check `is_active` (guards against accounts deactivated
      after a valid token was issued).
    - Provide a descriptive, consistent error message.
    """

    message = "Authentication credentials were not provided or are invalid."

    def has_permission(self, request: Request, view: APIView) -> bool:
        is_authenticated = super().has_permission(request, view)

        if not is_authenticated:
            return False

        if not request.user.is_active:
            self.message = "This account has been deactivated."
            return False

        return True
