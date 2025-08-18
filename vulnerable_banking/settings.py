import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# FLAW 2: Cryptographic Failures - Debug mode enabled in production
DEBUG = True  # Should be False in production
ALLOWED_HOSTS = ['*']  # Should be specific hosts

SECRET_KEY = 'django-insecure-your-secret-key-here'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'banking',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # FLAW 4: CSRF protection disabled
    # 'django.middleware.csrf.CsrfViewMiddleware',  # COMMENTED OUT - VULNERABILITY
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vulnerable_banking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vulnerable_banking.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# FLAW 4: A07:2021 - Identification and Authentication Failures
# Line 63: Weak password validation - All validators commented out - VULNERABILITY
AUTH_PASSWORD_VALIDATORS = [
    # All validators commented out allows weak passwords like "123"
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    #     'OPTIONS': {
    #         'min_length': 8,
    #     }
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# FLAW 4: A07:2021 - Identification and Authentication Failures  
# Line 81: No session timeout - Sessions last 1 year - VULNERABILITY
SESSION_COOKIE_AGE = 86400 * 365  # 1 year - VULNERABILITY
# FIX: SESSION_COOKIE_AGE = 1800  # 30 minutes

# FLAW 5: Logging disabled
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'