from django.db import models

class Exam(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
