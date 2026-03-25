import hashlib
import hmac
import os
import secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


DEFAULT_SALT = "medconnect-mobile-auth"


def hash_sensitive(value: str) -> str:
    secret = os.getenv("SECRET_KEY", "change-this-secret")
    return hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()


def generate_otp(length: int = 6) -> str:
    max_value = 10 ** length
    return f"{secrets.randbelow(max_value):0{length}d}"


def _serializer() -> URLSafeTimedSerializer:
    secret = os.getenv("SECRET_KEY", "change-this-secret")
    return URLSafeTimedSerializer(secret_key=secret, salt=DEFAULT_SALT)


def create_access_token(payload: dict) -> str:
    return _serializer().dumps(payload)


def verify_access_token(token: str, max_age_seconds: int = 86400) -> dict | None:
    try:
        return _serializer().loads(token, max_age=max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None
