from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = "exam"


class ExamAccessToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    is_used = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exam_access_token'
        constraints = [
            models.UniqueConstraint(fields=['exam', 'student'], name='unique_exam_student')
        ]



