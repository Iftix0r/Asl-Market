"""
Production settings — aslmarket.uz (cPanel Passenger WSGI)
cPanel username: asilmarket3
"""

from .settings import *  # noqa

import os
from pathlib import Path

# ─── Xavfsizlik ──────────────────────────────────────────────────────────────

DEBUG = False

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'aslmarket-prod-change-this-asap-2024!'
)

ALLOWED_HOSTS = [
    'aslmarket.uz',
    'www.aslmarket.uz',
    'localhost',
    '127.0.0.1',
]

# ─── Ma'lumotlar bazasi ───────────────────────────────────────────────────────
# Path(__file__) = /home/asilmarket3/<appfolder>/aslmarket/settings_production.py
# .parent        = /home/asilmarket3/<appfolder>/aslmarket/
# .parent.parent = /home/asilmarket3/<appfolder>/          ← loyiha root, db.sqlite3 shu yerda

BASE_DIR_PROD = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR_PROD / 'db.sqlite3',
    }
}

# ─── Static fayllar ──────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR_PROD / 'public' / 'static'
STATICFILES_DIRS = []   # collectstatic uchun bo'sh bo'lishi shart

# ─── Xavfsizlik headerlari ────────────────────────────────────────────────────

SECURE_BROWSER_XSS_FILTER   = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS             = 'SAMEORIGIN'

# ─── Logging: xatolar error.log ga yoziladi ───────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR_PROD / 'error.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
