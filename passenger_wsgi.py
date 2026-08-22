"""
passenger_wsgi.py — cPanel Passenger WSGI entry point

cPanel → Python App sozlamalarida:
  Application startup file: passenger_wsgi.py
  Application Entry point:  application
"""

import sys
import os

# ── Loyiha papkasini Python path ga qo'shing ──────────────────────────────────
# Bu yo'lni cPanel da loyiha joylashgan papkaga o'zgartiring
# Odatda: /home/<cpanel_username>/<app_folder>/
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ── Virtual environment ni faollashtirish ─────────────────────────────────────
# cPanel Python App avtomatik venv yaratadi.
# Quyidagi yo'lni cPanel ko'rsatgan venv yo'liga to'g'rilang.
# Odatda: /home/<cpanel_username>/virtualenv/<app_folder>/<python_version>/lib/pythonX.X/site-packages
VENV_PATH = os.path.join(PROJECT_DIR, 'venv')
if os.path.exists(VENV_PATH):
    activate = os.path.join(VENV_PATH, 'bin', 'activate_this.py')
    if os.path.exists(activate):
        with open(activate) as f:
            exec(f.read(), {'__file__': activate})

# ── Django sozlamalari ────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aslmarket.settings_production')

# ── WSGI application ──────────────────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
