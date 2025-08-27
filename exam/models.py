from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

def generate_token():
    return str(uuid.uuid4())

class Exam(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = "exam"


class ExamAccessToken(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    token = models.CharField(max_length=36, unique=True)
    is_used = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exam_access_token'
        constraints = [
            models.UniqueConstraint(fields=['exam', 'student'], name='unique_exam_student')
        ]



