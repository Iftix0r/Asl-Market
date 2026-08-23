"""
passenger_wsgi.py — cPanel Passenger WSGI entry point

cPanel → Setup Python App:
  Application startup file : passenger_wsgi.py
  Application Entry point  : application
"""

import sys
import os

# ── 1. Loyiha papkasi (bu fayl qayerda bo'lsa, shu papka) ────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ── 2. cPanel venv ni faollashtirish ─────────────────────────────────────────
# cPanel "Setup Python App" venv ni loyihadan TASHQARIDA saqlaydi:
#   /home/<user>/virtualenv/<app_root_relative>/<python_ver>/
# Masalan: /home/asilmarket3/virtualenv/aslmarket/3.11/
#
# WSGI_VENV_PATH env o'zgaruvchisi cPanel tomonidan avtomatik o'rnatiladi.
# Agar o'rnatilmagan bo'lsa — standart cPanel yo'lini urinamiz.

def _activate_venv():
    # Usul 1: cPanel WSGI_VENV_PATH (eng ishonchli)
    venv = os.environ.get('WSGI_VENV_PATH', '')
    if venv and os.path.isdir(venv):
        site_packages = os.path.join(venv, 'lib')
        if os.path.isdir(site_packages):
            for d in os.listdir(site_packages):
                sp = os.path.join(site_packages, d, 'site-packages')
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        return

    # Usul 2: Loyiha ichidagi venv (git da bo'lsa)
    local_venv = os.path.join(PROJECT_DIR, 'venv')
    activate = os.path.join(local_venv, 'bin', 'activate_this.py')
    if os.path.exists(activate):
        with open(activate) as f:
            exec(f.read(), {'__file__': activate})
        return

    # Usul 3: cPanel standart venv yo'li
    # /home/<user>/virtualenv/<folder_name>/<pyver>/
    try:
        username = os.path.basename(os.path.expanduser('~'))
        folder   = os.path.basename(PROJECT_DIR)
        for pyver in ('3.12', '3.11', '3.10', '3.9'):
            candidate = f'/home/{username}/virtualenv/{folder}/{pyver}'
            activate  = os.path.join(candidate, 'bin', 'activate_this.py')
            if os.path.exists(activate):
                with open(activate) as f:
                    exec(f.read(), {'__file__': activate})
                return
    except Exception:
        pass

_activate_venv()

# ── 3. Django settings ────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aslmarket.settings_production')

# ── 4. WSGI application ───────────────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
