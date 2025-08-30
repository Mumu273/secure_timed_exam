from celery import shared_task
from django.core.mail import send_mail
from decouple import config

@shared_task
def send_email_with_token(to_email, token, exam):
    subject = "Token for access exam"
    message = f"{token}\nThis is your access token for {exam} exam"
    from_email = config("EMAIL_HOST_USER")

    send_mail(subject, message, from_email, [to_email])
    print("------------> email sent.")
    return f"Email sent to {to_email}"
