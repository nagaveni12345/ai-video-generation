from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from text.text_improver import improve_text


class ImproveTextView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")

        if not text:
            return Response({"error": "Text required"}, status=400)

        improved = improve_text(text)

        return Response({
            "original_text": text,
            "improved_text": improved
        })

