from pathlib import Path
from datetime import timedelta
from decouple import config
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY")

# ─────────────────────────────────────────────────────────────
# BASE CONFIG
# ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────────────────────
SECRET_KEY = config("SECRET_KEY", default="unsafe-dev-key")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = []

# ─────────────────────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    # Local apps
    "users",
    "video",
    "avatars",
    "processing",
    "audio_generation",
]

# ─────────────────────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ─────────────────────────────────────────────────────────────
# URLS & TEMPLATES
# ─────────────────────────────────────────────────────────────
ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ─────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# ─────────────────────────────────────────────────────────────
# DJANGO REST FRAMEWORK
# ─────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ─────────────────────────────────────────────────────────────
# JWT CONFIGURATION
# ─────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("SECRET_KEY", default="unsafe-dev-key"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ─────────────────────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# ─────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────
# STATIC FILES
# ─────────────────────────────────────────────────────────────
STATIC_URL = "static/"

# ─────────────────────────────────────────────────────────────
# MEDIA FILES
# ─────────────────────────────────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ─────────────────────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────────────────────────────────────────────────
# ML PIPELINE PATH SETTINGS
# ─────────────────────────────────────────────────────────────
WAV2LIP_CHECKPOINT = config(
    "WAV2LIP_CHECKPOINT",
    default=str(BASE_DIR.parent / "ml_pipeline" / "models" / "checkpoints" / "wav2lip_gan.pth"),
)

ML_STORAGE_ROOT = config(
    "ML_STORAGE_ROOT",
    default=str(BASE_DIR.parent / "ml_pipeline" / "storage"),
)

ML_PROCESSED_ROOT = config(
    "ML_PROCESSED_ROOT",
    default=str(BASE_DIR.parent / "ml_pipeline" / "data" / "processed"),
)

# ─────────────────────────────────────────────────────────────
# TEXT VALIDATION SETTINGS
# ─────────────────────────────────────────────────────────────
MAX_TEXT_LENGTH = 5000
MIN_TEXT_LENGTH = 3

# ─────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] [{name}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "users": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "processing": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "ml_pipeline": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "wav2lip_inference": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "pro_landmark_merge": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "temporal_smoothing": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "render_final_video": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "lipsync_pipeline": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


MEDIA_URL = '/audio/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'audio')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ================================
# TEXT VALIDATION SETTINGS
# ================================
MAX_TEXT_LENGTH = 5000
MIN_TEXT_LENGTH = 3

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:8000"
)