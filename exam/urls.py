from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamAccessTokenAPIView

urlpatterns = [
    path(
        "exams/<exam_id>/generate-token/",
        ExamAccessTokenAPIView.as_view({"post": "create"}),
        name="generate-token",
    ),
    path(
        "exams/access/<token>/",
        ExamAccessTokenAPIView.as_view({"get": "validate_token"}),
        name="validate_token",
    ),
]
