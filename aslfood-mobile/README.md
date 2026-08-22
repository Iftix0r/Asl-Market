# AslFood Mobile — Android Ilovasi

AslMarket loyihasining fast-food bo'limi uchun React Native (Expo) asosida qurilgan Android ilovasi.

---

## Ilova Imkoniyatlari

### 👨‍🍳 Oshpaz / Admin Paneli
| Ekran | Funksiya |
|-------|----------|
| **Kitchen Board** | 4 ustunli Kanban: Yangi → Tayyorlanmoqda → Kuryerda → Yakunlandi. Har 10s avtomatik yangilanish, yangi buyurtma kelganda vibro bildirishnoma |
| **Menyu Boshqaruvi** | Barcha taomlar ro'yxati, bir teginishda Mavjud/Tugagan toggle, taom qo'shish, o'chirish |
| **Statistika** | Bugungi/haftalik/umumiy daromad, faol buyurtmalar soni, top-5 sotilgan taomlar |

### 🛍️ Mijoz Ilovasi
| Ekran | Funksiya |
|-------|----------|
| **Menyu & Savat** | Kategoriyalar filtri, taom kartalar, savat (+/-), animatsiyali savat tugmasi |
| **Buyurtma berish** | Dostavka / Olib ketish / Zalda — ism, telefon, manzil, holat kuzatish kodi |
| **Buyurtma kuzatish** | Kod kiritish, 4 bosqichli progress bar, tafsiolotlar |

---

## O'rnatish va Ishga Tushurish

### Talablar
- Node.js 18+
- Expo CLI: `npm install -g @expo/cli`
- Android qurilma yoki emulator

### Qadamlar

```bash
# 1. Papkaga kirish
cd "aslfood-mobile"

# 2. Paketlarni o'rnatish
npm install

# 3. Backend manzilini sozlash
# src/services/api.js faylini oching va BASE_URL ni o'zgartiring:
# export const BASE_URL = 'http://YOUR_SERVER_IP:8000';
# Misol: 'http://192.168.1.100:8000'

# 4. Django serverni ishga tushurish (alohida terminalda)
# cd "Asl Market"
# python manage.py runserver 0.0.0.0:8000

# 5. Expo ni ishga tushurish
npm run android
# yoki
npm start   # keyin QR kodni Expo Go ilovasi bilan skanerlang
```

### BASE_URL ni topish

Django server bilan bir Wi-Fi da bo'lganingizda:

```bash
# Linux/Mac
ip addr show | grep "inet "

# Windows
ipconfig
```

Chiqgan IP manzilni `src/services/api.js` dagi `BASE_URL` ga qo'ying.

---

## Fayl Tuzilmasi

```
aslfood-mobile/
├── App.js                          # Entry point
├── app.json                        # Expo konfiguratsiya
├── package.json                    # Paketlar
├── babel.config.js
└── src/
    ├── navigation/
    │   └── AppNavigator.js         # Stack + Tab navigatsiya
    ├── screens/
    │   ├── HomeScreen.js           # Mode tanlash (Oshpaz vs Mijoz)
    │   ├── KitchenScreen.js        # 🍳 Kanban buyurtmalar board
    │   ├── MenuScreen.js           # 🍔 Menyu boshqaruvi
    │   ├── AddMenuItemScreen.js    # ➕ Yangi taom qo'shish
    │   ├── StatsScreen.js          # 📊 Daromad statistikasi
    │   ├── CustomerMenuScreen.js   # 🛍️ Mijoz menyu & savat
    │   └── OrderTrackingScreen.js  # 📍 Buyurtma kuzatish
    ├── components/
    │   ├── Toast.js                # Global bildirishnomalar
    │   ├── StatusBadge.js          # Holat ko'rsatkichi
    │   └── LoadingOverlay.js       # Yuklash ekrani
    ├── services/
    │   └── api.js                  # Barcha API so'rovlar
    └── utils/
        ├── colors.js               # Rang palitras
        └── format.js               # Formatlash funksiyalar
```

---

## Backend API Endpointlar

Django backendda `store/urls.py` ga qo'shilgan:

| Method | URL | Tavsif |
|--------|-----|--------|
| GET | `/api/food/menu/` | Mavjud taomlar (mijoz uchun) |
| GET | `/api/food/menu/all/` | Barcha taomlar (admin uchun) |
| POST | `/api/food/menu/add/` | Yangi taom qo'shish |
| POST | `/api/food/menu/edit/<id>/` | Taomni tahrirlash |
| POST | `/api/food/menu/delete/<id>/` | Taomni o'chirish |
| POST | `/api/food/menu/toggle/<id>/` | Mavjud/Tugagan toggle |
| GET | `/api/food/categories/` | Kategoriyalar |
| GET | `/api/food/orders/` | Buyurtmalar ro'yxati |
| POST | `/api/food/orders/place/` | Yangi buyurtma berish |
| POST | `/api/food/orders/status/` | Holat yangilash |
| GET | `/api/food/orders/<id>/` | Buyurtma tafsiloti |
| GET | `/api/food/orders/track/<code>/` | Kod bo'yicha kuzatish |
| GET | `/api/food/stats/` | Statistika |

---

## APK Qurish (Production)

```bash
# EAS Build bilan (Expo)
npm install -g eas-cli
eas login
eas build --platform android --profile preview
```

`eas.json` fayli:
```json
{
  "build": {
    "preview": {
      "android": {
        "buildType": "apk"
      }
    }
  }
}
```

---

## Muammo va Yechimlar

**"Network request failed" xatosi:**
- Django server `0.0.0.0:8000` da ishlayotganligini tekshiring
- `BASE_URL` dagi IP to'g'riligini tekshiring
- Qurilma va server bir Wi-Fi da ekanini tekshiring
- Android emulatorda `http://10.0.2.2:8000` ishlatish kerak

**Yangi buyurtma bildirishnomasi ishlamayapti:**
- Android qurilmada "Do Not Disturb" o'chirilganligini tekshiring

**Menyu yuklanmayapti:**
- `/api/food/menu/seed/` ga o'tib demo ma'lumot qo'shing
