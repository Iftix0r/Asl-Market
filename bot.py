"""
AslFood Telegram Bot
====================
Ishga tushirish:
    python bot.py

Talab qilinadi:
    pip install python-telegram-bot>=21.0

Settings.py da sozlash kerak:
    TELEGRAM_BOT_TOKEN = "..."
    TELEGRAM_GROUP_CHAT_ID = "-100..."
    WEBAPP_BASE_URL = "https://yourdomain.com"
"""

import asyncio
import sys
import os

# Django sozlamalarini yuklash (agar bot alohida ishlatilsa)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aslmarket.settings")

import django
django.setup()

from django.conf import settings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

BOT_TOKEN     = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL    = getattr(settings, "WEBAPP_BASE_URL", "").rstrip("/") + "/"
GROUP_CHAT_ID = getattr(settings, "TELEGRAM_GROUP_CHAT_ID", "")

# ConversationHandler holati
WAITING_PHONE = 1


# =====================================================
# Yordamchi: BotUser DB ga saqlash / yangilash
# =====================================================
async def _upsert_bot_user(user) -> None:
    """
    Har bir /start, /menu yoki xabar kelganda foydalanuvchini
    DB ga yozadi yoki mavjud bo'lsa yangilaydi.
    """
    from store.models import BotUser
    from asgiref.sync import sync_to_async
    from django.utils import timezone

    if not user:
        return

    # Profil rasmi URL ni olishga urinish (bot token bilan)
    photo_url = None
    try:
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        photos = await bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    except Exception:
        pass  # Rasm olish ixtiyoriy — xato bo'lsa o'tkazib yuborish

    def _save():
        obj, created = BotUser.objects.get_or_create(
            telegram_id=str(user.id),
            defaults={
                'first_name':    user.first_name or '',
                'last_name':     user.last_name  or '',
                'username':      user.username,
                'language_code': user.language_code,
                'photo_url':     photo_url,
                'joined_at':     timezone.now(),
                'last_seen':     timezone.now(),
            }
        )
        if not created:
            # Mavjud bo'lsa — ma'lumotlarni yangilash
            obj.first_name    = user.first_name or ''
            obj.last_name     = user.last_name  or ''
            obj.username      = user.username
            obj.language_code = user.language_code
            obj.last_seen     = timezone.now()
            if photo_url:
                obj.photo_url = photo_url
            obj.save(update_fields=[
                'first_name', 'last_name', 'username',
                'language_code', 'last_seen', 'photo_url'
            ])
        return obj

    await sync_to_async(_save)()


# =====================================================
# /start — Foydalanuvchini kutib olish + Web App tugmasi
# =====================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    first_name = user.first_name if user else "Mehmon"

    # Foydalanuvchini DB ga saqlash / yangilash
    await _upsert_bot_user(user)

    keyboard = [
        [
            InlineKeyboardButton(
                text="🍔 Menyu va Buyurtma Berish",
                web_app=WebAppInfo(url=WEBAPP_URL),
            )
        ],
        [
            InlineKeyboardButton("📞 Bog'lanish", url="https://t.me/aslfoodsupport"),
            InlineKeyboardButton("ℹ️ Haqimizda", callback_data="about"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Assalomu alaykum, <b>{first_name}</b>! 👋\n\n"
        f"🍔 <b>AslFood</b> botiga xush kelibsiz!\n\n"
        f"Bizning menyumizdan mazali taomlarni tanlang va "
        f"<b>15–25 daqiqada</b> dostavka qilib beramiz 🛵\n\n"
        f"👇 <b>«Menyu va Buyurtma Berish»</b> tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


# =====================================================
# /menu — Tezkor menyu tugmasi
# =====================================================
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _upsert_bot_user(update.effective_user)
    keyboard = [
        [InlineKeyboardButton("🍔 Menyuni ochish", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    await update.message.reply_text(
        "🍽️ <b>AslFood Menyu</b>\n\nQuyidagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =====================================================
# /orders — Faol buyurtmalar ro'yxati (oshpaz uchun)
# =====================================================
async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Faqat guruh adminlari ko'ra oladi"""
    from store.models import FoodOrder
    from asgiref.sync import sync_to_async

    active = await sync_to_async(list)(
        FoodOrder.objects.filter(
            status__in=["new", "preparing", "delivering"]
        ).order_by("created_at")[:10]
    )

    if not active:
        await update.message.reply_text("✅ Hozircha faol buyurtmalar yo'q.")
        return


    STATUS_EMOJI = {
        "new": "🟡 Yangi",
        "preparing": "🍳 Tayyorlanmoqda",
        "delivering": "🛵 Yo'lda",
    }

    text = "📋 <b>Faol buyurtmalar:</b>\n\n"
    for o in active:
        text += (
            f"#{o.order_code} — {o.customer_name} ({o.phone})\n"
            f"   📊 {STATUS_EMOJI.get(o.status, o.status)} | 💰 {int(o.total_amount):,} so'm\n\n"
        )

    await update.message.reply_text(text, parse_mode="HTML")


# =====================================================
# Callback Query — Haqimizda
# =====================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.message.reply_text(
            "🍔 <b>AslFood</b>\n\n"
            "Biz tez va mazali taomlar yetkazib beramiz.\n"
            "Lavash, Pizza, Gamburger va ko'p boshqa taomlar!\n\n"
            "📍 Manzil: ...\n"
            "📞 Tel: ...\n"
            "🕒 Ish vaqti: 09:00 — 23:00",
            parse_mode="HTML",
        )


# =====================================================
# Web App ma'lumotlari (ixtiyoriy — tg.sendData orqali)
# =====================================================
async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Agar Mini App tg.sendData() ishlatsa"""
    data = update.message.web_app_data.data
    await update.message.reply_text(f"✅ Web App dan ma'lumot keldi:\n{data}")


# =====================================================
# Noma'lum xabar — Foydalanuvchiga yo'naltirish
# =====================================================
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🍔 Menyuni ochish", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    await update.message.reply_text(
        "Menyu uchun /start yoki /menu buyrug'ini yuboring 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =====================================================
# Application Factory
# =====================================================
def create_bot_app() -> Application:
    """Telegram application bot factory (used for both polling and webhook)."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        return None

    app = Application.builder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    return app


# =====================================================
# MAIN — Bot ishga tushirish (Polling yoki Webhook Sozlash)
# =====================================================
def main() -> None:
    import argparse
    import urllib.request
    import urllib.parse
    import json

    parser = argparse.ArgumentParser(description="AslFood Telegram Bot")
    parser.add_argument("--set-webhook", type=str, help="Telegram Webhook URL'ini o'rnatish (masalan, https://aslmarket.uz/api/telegram/webhook/)")
    parser.add_argument("--delete-webhook", action="store_true", help="Telegram Webhook'ni o'chirish (Polling'ga qaytish)")
    parser.add_argument("--webhook-info", action="store_true", help="Mavjud Webhook holatini ko'rish")
    args = parser.parse_args()

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ XATO: settings.py da TELEGRAM_BOT_TOKEN to'ldirilmagan!")
        sys.exit(1)

    if args.set_webhook:
        url = f"https://api.telegram.org/bot{token}/setWebhook?url={urllib.parse.quote(args.set_webhook)}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                print(f"✅ Webhook natijasi: {res}")
        except Exception as e:
            print(f"❌ Xato: {e}")
        return

    if args.delete_webhook:
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                print(f"✅ Webhook o'chirildi: {res}")
        except Exception as e:
            print(f"❌ Xato: {e}")
        return

    if args.webhook_info:
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                print(f"ℹ️ Webhook Ma'lumoti: {json.dumps(res, indent=2)}")
        except Exception as e:
            print(f"❌ Xato: {e}")
        return

    if not WEBAPP_URL or "yourdomain" in WEBAPP_URL:
        print("⚠️  OGOHLANTIRISH: WEBAPP_BASE_URL to'ldirilmagan yoki placeholder.")

    print(f"🤖 AslFood Bot Polling rejimida ishga tushmoqda...")
    print(f"   Web App URL: {WEBAPP_URL}")
    print(f"   Guruh ID   : {GROUP_CHAT_ID}")

    app = create_bot_app()
    if not app:
        print("❌ Bot ilovasini yaratib bo'lmadi.")
        sys.exit(1)

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()

