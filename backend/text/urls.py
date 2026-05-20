from django.urls import path
from .views import ImproveTextView

urlpatterns = [
    path("improve-text/", ImproveTextView.as_view()),
]