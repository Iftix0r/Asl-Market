"""
Production settings — aslmarket.uz (cPanel Passenger WSGI)

Faqat server uchun. Lokal ishlatmang.
"""

from .settings import *  # noqa: bazaviy sozlamalar import

import os
from pathlib import Path

# ─── Xavfsizlik ──────────────────────────────────────────────────────────────

DEBUG = False

# cPanel dan environment variable orqali yoki to'g'ridan-to'g'ri kiriting
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'change-this-to-a-new-random-secret-key-before-use'
)

ALLOWED_HOSTS = [
    'aslmarket.uz',
    'www.aslmarket.uz',
]

# ─── Ma'lumotlar bazasi ───────────────────────────────────────────────────────
# cPanel da SQLite fayl yo'lini to'liq ko'rsating
# /home/<cpanel_username>/aslmarket/db.sqlite3

BASE_DIR_PROD = Path(os.environ.get(
    'DJANGO_BASE_DIR',
    '/home/host7905/aslmarket'
))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR_PROD / 'db.sqlite3',
    }
}

# ─── Static fayllar ──────────────────────────────────────────────────────────
# python manage.py collectstatic ishga tushirilganda fayllar shu yerga yig'iladi

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR_PROD / 'public' / 'static'
STATICFILES_DIRS = []  # collectstatic bilan ishlash uchun bo'sh bo'lishi kerak

# ─── Xavfsizlik sozlamalari ───────────────────────────────────────────────────

SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = 'SAMEORIGIN'

# HTTPS ishlatilsa (tavsiya etiladi):
# SESSION_COOKIE_SECURE   = True
# CSRF_COOKIE_SECURE      = True
# SECURE_SSL_REDIRECT     = True

# ─── Loglar ──────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR_PROD / 'error.log',
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
