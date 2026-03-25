import os


class BaseConfig:
    """
    Base configuration shared across environments
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")

    # Database (DB-agnostic)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Flask settings
    DEBUG = False
    TESTING = False

    # Session & Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    # OTP Settings
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))
    OTP_MAX_RETRIES = int(os.getenv("OTP_MAX_RETRIES", 3))

    # Rate limiting
    IVR_RATE_LIMIT = os.getenv("IVR_RATE_LIMIT", "10/minute")

    # Notification APIs
    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "mock")
    WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "mock")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


def get_config():
    """
    Returns config class based on ENV variable
    """
    env = os.getenv("FLASK_ENV", "development").lower()

    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
