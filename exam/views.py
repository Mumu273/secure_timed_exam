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
from external.generate_token import generate_token
from external.validate_token import token_validation
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .tasks import send_email_with_token

class CustomUserThrottle(UserRateThrottle):
    rate = '5/minute'

class CustomAnonThrottle(AnonRateThrottle):
    rate = '3/minute'


class ExamAccessTokenAPIView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_throttles(self):
        if self.action == 'validate_token':
            return [CustomUserThrottle(), CustomAnonThrottle()]
        return super().get_throttles()


    @extend_schema(
        request=GenerateExamAccessTokenSerializer,
        examples=[
            OpenApiExample(
                "Generate Token",
                value={
                    "student_id": 0,
                    "valid_minutes": 0,
                },
                request_only=True,
            )
        ],
    )

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        request_data = request.data
        if request_data['valid_minutes'] < 0:
            return Response({"detail": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)
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

    @extend_schema(
        request=TokenValidateSerializer,
        examples=[
            OpenApiExample(
                "Validate Token",
                value={
                    "student": 0,
                    "exam": 0,
                },
                request_only=True,
            )
        ],
    )
    def validate_token(self, request, *args, **kwargs):
        status_code = status.HTTP_403_FORBIDDEN
        token = ExamAccessToken.objects.filter(token=kwargs['token']).first()

        validate_token = token_validation(token)

        if not validate_token['is_valid']:
            return Response({"detail": validate_token["detail"]}, status=status_code)

        email = token.student.email
        email_token = kwargs["token"]
        exam = token.exam.title
        send_email_with_token.delay(email, email_token, exam)


        token.is_used = True
        token.save()

        serializer = TokenValidateSerializer(token, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)



