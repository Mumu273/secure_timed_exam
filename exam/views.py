from datetime import timedelta

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .models import ExamAccessToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.utils import timezone
from rest_framework.permissions import AllowAny

class ExamAccessTokenAPIView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        request=GenerateExamAccessTokenSerializer,
        examples=[
            OpenApiExample(
                "Generate Token",
                value={
                    "student_id": "float",
                    "valid_minutes": "float",
                },
                request_only=True,
            )
        ],
    )

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        request_data = request.data
        user = User.objects.filter(id=request_data['student_id']).first()
        exam = Exam.objects.filter(id=kwargs['exam_id']).first()
        if not (user and exam):
            return Response({"detail": "Invalid exam or student."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        post_data = {
            "exam": kwargs['exam_id'],
            "student": request_data['student_id'],
            "token": generate_token(),
            "valid_from": now,
            "valid_until": now + timedelta(minutes=request_data['valid_minutes'])
        }
        exam_token = ExamAccessToken.objects.filter(student=post_data['student'], exam=post_data['exam']).first()
        if exam_token:
            return Response({"detail": "Token already exists for this student and exam"})
        serializer = ExamAccessTokenSerializer(data=post_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"token": serializer.validated_data['token'], "message": "Token Generated Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


    def validate_token(self, request, *args, **kwargs):
        status_code = status.HTTP_403_FORBIDDEN
        token = ExamAccessToken.objects.filter(token=kwargs['token']).first()
        if not token:
            return Response({"detail": "Invalid token"}, status=status_code)

        now = timezone.now()

        if not token.valid_from <= now < token.valid_until:
            return Response({"detail": "This access link has expired"}, status=status_code)

        if token.is_used:
            return Response({"detail": "Token already used"}, status=status_code)

        token.is_used = True
        token.save()

        serializer = TokenValidateSerializer(token, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)



