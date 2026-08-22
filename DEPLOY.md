# aslmarket.uz — cPanel Deploy Qo'llanmasi

## 1. cPanel → Python App yaratish

1. cPanel ga kiring → **"Setup Python App"** (yoki "Python App")
2. **Create Application** tugmasini bosing:
   - Python version: **3.11** (yoki mavjud eng yangi)
   - Application root: `aslmarket`  ← server papka nomi
   - Application URL: `aslmarket.uz`
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
3. **Create** tugmasini bosing

---

## 2. Fayllarni serverga yuklash

### Git orqali (tavsiya etiladi):
```bash
# SSH orqali serverga kiring
ssh username@aslmarket.uz

# Papkaga kiring
cd ~/aslmarket

# Git clone
git clone https://github.com/sizning-repo/Asl-Market.git .
```

### yoki File Manager orqali:
cPanel → File Manager → `aslmarket/` papkasiga barcha fayllarni yuklang

---

## 3. Virtual Environment da paketlarni o'rnatish

cPanel Python App sahifasida:
1. **"Run Pip Install"** yoki terminal orqali:

```bash
# cPanel terminal (SSH)
cd ~/aslmarket
source ~/virtualenv/aslmarket/3.11/bin/activate

pip install -r requirements.txt
```

---

## 4. settings_production.py ni sozlash

```bash
# SSH terminalda
nano ~/aslmarket/aslmarket/settings_production.py
```

O'zgartiring:
- `SECRET_KEY` — yangi tasodifiy kalit (quyida generator)
- `BASE_DIR_PROD` — `/home/SIZNING_CPANEL_USERNAME/aslmarket`
- `ALLOWED_HOSTS` — `['aslmarket.uz', 'www.aslmarket.uz']`

**Yangi SECRET_KEY yaratish:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 5. Ma'lumotlar bazasini sozlash

```bash
cd ~/aslmarket
source ~/virtualenv/aslmarket/3.11/bin/activate

# Migratsiyalar
python manage.py migrate --settings=aslmarket.settings_production

# Admin yaratish
python manage.py createsuperuser --settings=aslmarket.settings_production

# Demo ma'lumot (ixtiyoriy)
# Brauzerda: https://aslmarket.uz/panel/seed/
# va https://aslmarket.uz/aslfood/panel/seed/
```

---

## 6. Statik fayllarni yig'ish

```bash
cd ~/aslmarket
source ~/virtualenv/aslmarket/3.11/bin/activate

python manage.py collectstatic --settings=aslmarket.settings_production --noinput
```

Bu barcha CSS/JS fayllarni `public/static/` papkasiga ko'chiradi.

---

## 7. passenger_wsgi.py ni tekshirish

`passenger_wsgi.py` ichidagi yo'lni tekshiring:

```python
# Bu qator to'g'ri bo'lishi kerak:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aslmarket.settings_production')
```

---

## 8. Ilovani restart qilish

cPanel → Python App → **Restart** tugmasi

---

## 9. Tekshirish

Brauzerda:
- https://aslmarket.uz/ — storefront
- https://aslmarket.uz/panel/ — admin panel
- https://aslmarket.uz/admin/ — Django admin
- https://aslmarket.uz/api/food/menu/ — JSON API (mobil ilova)

---

## Muammo va yechimlar

### 500 Internal Server Error
```bash
# Xato loglarni ko'rish
cat ~/aslmarket/error.log
# yoki
cat ~/logs/aslmarket.uz.error.log
```

### Static fayllar ko'rinmayapti
```bash
python manage.py collectstatic --settings=aslmarket.settings_production
```
Keyin cPanel → Python App → Restart

### "ModuleNotFoundError: No module named 'django'"
Virtual environment to'g'ri faollashtirilmagan.
`passenger_wsgi.py` dagi `VENV_PATH` ni cPanel ko'rsatgan yo'lga o'zgartiring.
cPanel Python App sahifasida virtual environment yo'lini ko'rasiz.

---

## Fayl tuzilmasi (serverda)

```
~/aslmarket/                    ← Application root (cPanel da)
├── passenger_wsgi.py           ← Passenger entry point ✅
├── manage.py
├── requirements.txt
├── db.sqlite3                  ← Ma'lumotlar bazasi (avtomatik yaratiladi)
├── error.log                   ← Xato loglari
├── aslmarket/
│   ├── settings.py             ← Asosiy sozlamalar
│   ├── settings_production.py  ← Production sozlamalar ✅
│   ├── urls.py
│   └── wsgi.py
├── store/
├── templates/
├── static/                     ← Manba static fayllar
└── public/
    └── static/                 ← collectstatic chiqishi
```
