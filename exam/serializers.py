from rest_framework import serializers
from .models import ExamAccessToken, Exam, User

class GenerateExamAccessTokenSerializer(serializers.Serializer):
    student_id = serializers.FloatField()
    valid_minutes = serializers.FloatField()

    class Meta:
        fields = ['student_id', 'valid_minutes']


class ExamAccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAccessToken
        fields = '__all__'


class TokenValidateSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    exam = serializers.SerializerMethodField()

    def get_student(self, obj):
        user = User.objects.filter(id=obj.student).first()
        data = {
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email
        }
        return data

    def get_exam(self, obj):
        exam = Exam.objects.filter(id=obj.exam).first()
        data = {
            "title": exam.title,
            "start_time": exam.start_time,
            "end_time": exam.end_time
        }
        return data


    class Meta:
        model = ExamAccessToken
        fields = ['exam', 'student']
