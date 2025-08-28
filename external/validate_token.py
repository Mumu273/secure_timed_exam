from django.utils import timezone


def token_validation(token):
    if not token:
        return {"is_valid": False, "detail": "Invalid token"}

    now = timezone.now()

    if not token.valid_from <= now < token.valid_until:
        return {"is_valid": False, "detail": "This access link has expired"}

    if token.is_used:
        return {"is_valid": False, "detail": "Token already used"}

    return {"is_valid": True}