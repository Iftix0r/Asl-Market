# Asl Market & AslFood — To'liq Loyiha Hujjatlanishi (Documentation)

Ushbu loyiha **Asl Market** (chakana savdo va POS kassa tizimi) hamda **AslFood** (fast-food, restoran va taom yetkazib berish Web & Mobil platformasi) dan iborat kompleks boshqaruv va savdo tizimidir.

---

## 🎯 Loyihaning Umumiy Maqsadi (Purpose)

Loyihaning asosiy maqsadi — do'konlar, chakana savdo nuqtalari, kafellar, fast-food va restoranlar uchun:
1. **POS Kassa va Chakana Savdo:** Mahsulotlar ombori, shtrix-kod orqali tezkor sotuv, chek chiqarish, nasiya/qarz daftarini yuritish va tahliliy hisobotlar (analytics).
2. **AslFood (Fast Food & Restoran):** Onlayn taom zakaz qilish, oshxona va kuryerlar uchun buyurtmalar pipelini (statuslar boshqaruvi), menyu va retseptlar boshqaruvi.
3. **Mobil Ilova (AslFood Mobile App):** Mijozlar va adminlar uchun React Native (Expo) dagi mobil ilova va REST API infratuzilmasi.

---

## 🧱 Texnologiyalar Steki (Tech Stack)

* **Backend Framework:** Python 3.11, Django 4.2.17
* **Database:** SQLite3 (`db.sqlite3`)
* **REST API:** Django View-based JSON API (Mobile App uchun)
* **Frontend Web:** HTML5, CSS3 (Glassmorphism design system), JavaScript, Bootstrap, Chart.js
* **Mobile App:** React Native, Expo, Axios, React Navigation
* **Deployment/Server:** cPanel, LiteSpeed / Passenger WSGI (`passenger_wsgi.py`)

---

## 🚀 Loyihadagi Mavjud Modullar va Imkoniyatlar (Features & Modules)

### 1. 🛒 AslMarket (Chakana Savdo va POS Kassa System)
* **Storefront (`/`):** Online xaridorlar uchun mahsulotlar vitrinasi va savatcha (checkout) tizimi.
* **POS Kassa (`/panel/pos/`):** Kassirlar uchun mo'ljallangan interfeys:
  * Shtrix-kod (SKU) va nom bo'yicha tezkor qidiruv.
  * To'lov turlari: Naqd pul, Bank kartasi, Nasiya (Qarzga sotish).
  * Chek yaratish va chop etish.
* **Mahsulotlar Ombori (`/panel/products/`):**
  * Mahsulot qo'shish, tahrirlash, o'chirish.
  * Sotish narxi va Tan narxi (Cost price) hisobi.
  * Kam qolgan mahsulotlar ogohlantirishi (Low stock warning <= 5).
  * Shtrix-kod va Rasm havolalari.
* **Qarzdorlar / Nasiya Daftari (`/panel/debtors/`):**
  * Qarzdorlarni ro'yxatga olish (F.I.SH, Telefon, Boshlang'ich qarz, Qaytarish muddati, Izoh).
  * To'lovlarni qabul qilish va to'lovlar tarixini yuritish.
  * Qarz muddati o'tganligini vizual ko'rsatish: Normal (<7 kun), Ogohlantirish (7-30 kun), Shoshilinch (>30 kun).
  * Qarzdorlik chekini chop etish va CSV formatida eksport qilish (`/panel/debtors/export/`).
* **Sotuvlar Tarixi & Eksport (`/panel/sales/`):**
  * Barcha sotuvlar ro'yxati (Chek kodi, to'lov usuli, umumiy summa).
  * Sotuvlarni CSV ga eksport qilish (`/panel/sales/export/`).
* **Analitika va Dashboard (`/panel/`, `/panel/analytics/`):**
  * Jami tushum, jami qarzlar summasi, sof foyda (Profit) kalkulyatsiyasi.
  * Eng ko'p sotilgan mahsulotlar va sotuv grafiklari (Chart.js).

---

### 2. 🍔 AslFood (Fast-Food va Restoran Tizimi)
* **Oshxona Dashboard (`/aslfood/panel/`):** Real-vaqt rejimida kelayotgan buyurtmalarni kuzatish va ularning holatini (status) o'zgartirish:
  * 🟡 **Yangi Buyurtma** (`new`)
  * 🍳 **Tayyorlanmoqda** (`preparing`)
  * 🛵 **Yo'lda / Kuryerda** (`delivering`)
  * ✅ **Topshirildi** (`completed`)
  * 🔴 **Bekor qilindi** (`cancelled`)
* **Menyu Boshqaruvi (`/aslfood/panel/menu/`):**
  * Yangi taomlar qo'shish (Narx, Tayyorlanish vaqti daqiqada, Tarkib/Retsept, Rasm).
  * Taom mavjudligi / tugaganligini bir bosishda yoqish/o'chirish (`toggle_availability`).
* **Chek Bosish (`/aslfood/panel/receipt/<id>/`):** Oshxona va kuryer uchun taom buyurtmasi chekini bosish.
* **Onlayn Buyurtma Berish API (`/aslfood/order/`):** Veb-saytdan taom buyurtma qilish integratsiyasi.

---

### 3. 📱 AslFood Mobile App (`/aslfood-mobile/`)
* React Native (Expo) ilovasi.
* Restoran menyusini ko'rish, taomlarni savatchaga qo'shish va onlayn buyurtma berish.
* Buyurtma kodi (`order_code`) bo'yicha taom holatini (status) real-vaqt rejimida kuzatish (Order Tracker).
* REST API Endpoints:
  * `GET /api/food/menu/` — Mavjud menyular ro'yxati
  * `POST /api/food/orders/place/` — Yangi buyurtma joylash
  * `GET /api/food/orders/track/<code_id>/` — Buyurtma statusini tekshirish
  * `POST /api/food/orders/status/` — Buyurtma statusini yangilash (Admin/Oshxona uchun)
  * `GET /api/food/stats/` — Fast-food analitikasi

---

## 📂 Loyiha Papkalar Tuzilishi (Directory Structure)

```
Asl Market/
├── manage.py                   # Django CLI boshqaruv fayli
├── passenger_wsgi.py           # cPanel/LiteSpeed hosting entry point
├── requirements.txt            # Python kutubxonalari (Django==4.2.17)
├── DEPLOY.md                   # cPanel ga joylash bo'yicha to'liq qo'llanma
├── README.md                   # Loyiha haqida to'liq hujjat (Ushbu fayl)
├── db.sqlite3                  # Ma'lumotlar bazasi
│
├── aslmarket/                  # Loyiha sozlamalari
│   ├── settings.py             # Asosiy Django sozlamalari
│   ├── settings_production.py  # Production (cPanel) sozlamalari
│   ├── urls.py                 # Asosiy URL yo'naltirgichlar
│   └── wsgi.py / asgi.py
│
├── store/                      # Asosiy ilova (App)
│   ├── models.py               # Database modellari (Category, Product, Debtor, Payment, Sale, FoodItem, FoodOrder...)
│   ├── views.py                # Barcha biznes-mantiq va REST API logic
│   ├── urls.py                 # URL yo'nalishlar (Store, POS, Debtor, AslFood, API)
│   └── admin.py                # Django Admin paneli moslashuvi
│
├── templates/                  # HTML shablonlar
│   ├── storefront.html         # Chakana store vitrinasi
│   ├── panel/                  # Market Admin panel (dashboard, pos, products, debtors, sales, analytics)
│   └── aslfood/                # AslFood Oshxona panel (dashboard, menu, receipt)
│
├── static/                     # CSS, JS, Rasmlar
├── public/                     # Production static yig'ish papkasi (collectstatic)
│
└── aslfood-mobile/             # React Native (Expo) Mobil Ilovasi
    ├── App.js
    ├── package.json
    └── src/                    # Mobile app komponentlari va ekranlari
```

---

## 🛠️ Ma'lumotlar Bazasi Modellari (Data Models Summary)

1. **`Category`** & **`Product`**: Mahsulotlar, narx, tan narx, ombor qoldig'i (`stock`), shtrix-kod, low-stock hisobi.
2. **`Debtor`** & **`Payment`**: Qarzdorlar ismi, telefoni, jami qarz, muddat, o'tgan kunlar va shoshilinchlik darajasi (`overdue_level`), to'lovlar tarixi (`Payment`).
3. **`Sale`** & **`SaleItem`**: POS sotuvlari, chek kodi, to'lov usuli (Naqd/Karta/Nasiya), sotilgan mahsulotlar.
4. **`FoodCategory`**, **`FoodItem`**, **`FoodOrder`**, **`FoodOrderItem`**: Fast-food taomlari, tayyorlanish vaqti, mavjudligi, buyurtma turi (dostavka/pickup/table) va statusi.

---

## ⚡ Ishga tushirish (Local Setup)

```bash
# 1. Virtual muhit yaratish va faollashtirish
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3. Bazani tayyorlash va migratsiya
python manage.py migrate

# 4. Serverni ishga tushirish
python manage.py runserver
```

---

## 🚀 Serverga Joylash (Deployment)
Serverga (cPanel / SSH) joylash tartibi **`DEPLOY.md`** faylida to'liq bosqichma-bosqich yozilgan.
