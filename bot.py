"""
AslFood Telegram Bot
====================
Ishga tushirish:
    python bot.py

Talab qilinadi:
    pip install python-telegram-bot>=21.0

settings.py:
    TELEGRAM_BOT_TOKEN      = "..."
    TELEGRAM_GROUP_CHAT_ID  = "-100..."
    WEBAPP_BASE_URL         = "https://yourdomain.com"
    TELEGRAM_ADMIN_IDS      = [123456789]
"""

import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aslmarket.settings")
import django
django.setup()

from django.conf import settings
from telegram import (
    Update,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from store.telegram_ui import (
    admin_inline_keyboard,
    admin_reply_keyboard,
    customer_inline_keyboard,
    customer_webapp_url,
    is_admin,
)

BOT_TOKEN     = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL    = customer_webapp_url()
GROUP_CHAT_ID = getattr(settings, "TELEGRAM_GROUP_CHAT_ID", "")

WAITING_PHONE = 1


def _inline(data: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup.de_json(data, None)


def _reply(data: dict) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup.de_json(data, None)


def _customer_kb() -> InlineKeyboardMarkup:
    return _inline(customer_inline_keyboard())


async def _send_admin_home(message, first_name: str) -> None:
    await message.reply_text(
        f"Assalomu alaykum, <b>{first_name}</b>! 👋\n\n"
        f"🛠 <b>AslFood Admin</b>\n\n"
        f"Oshxona, buyurtmalar, taomlar, mijozlar va qarzdorlar — "
        f"hammasi botdagi <b>Admin panel</b> Web App orqali.\n"
        f"Yangi buyurtmalar shu chatga ham keladi.",
        parse_mode="HTML",
        reply_markup=_reply(admin_reply_keyboard()),
    )
    await message.reply_text(
        "👇 Bo'limni tanlang:",
        reply_markup=_inline(admin_inline_keyboard()),
    )


async def _upsert_bot_user(user, phone: str = None):
    from store.models import BotUser
    from asgiref.sync import sync_to_async
    from django.utils import timezone

    if not user:
        return None

    photo_url = None
    try:
        from telegram import Bot as TgBot
        tg_bot = TgBot(token=BOT_TOKEN)
        photos = await tg_bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            f = await tg_bot.get_file(photos.photos[0][-1].file_id)
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f.file_path}"
    except Exception:
        pass

    def _save():
        obj, created = BotUser.objects.get_or_create(
            telegram_id=str(user.id),
            defaults={
                'first_name':    user.first_name or '',
                'last_name':     user.last_name  or '',
                'username':      user.username,
                'language_code': user.language_code,
                'photo_url':     photo_url,
                'phone':         phone,
                'joined_at':     timezone.now(),
                'last_seen':     timezone.now(),
            }
        )
        if not created:
            fields = ['last_seen']
            obj.last_seen     = timezone.now()
            obj.first_name    = user.first_name or obj.first_name
            obj.last_name     = user.last_name  or obj.last_name
            obj.username      = user.username   or obj.username
            obj.language_code = user.language_code or obj.language_code
            fields += ['first_name', 'last_name', 'username', 'language_code']
            if photo_url:
                obj.photo_url = photo_url
                fields.append('photo_url')
            if phone and not obj.phone:
                obj.phone = phone
                fields.append('phone')
            obj.save(update_fields=fields)
        return obj

    return await sync_to_async(_save)()


def _has_phone(user_id: int) -> bool:
    from store.models import BotUser
    return BotUser.objects.filter(
        telegram_id=str(user_id), phone__isnull=False
    ).exclude(phone='').exists()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user       = update.effective_user
    first_name = user.first_name if user else "Mehmon"

    await _upsert_bot_user(user)

    from asgiref.sync import sync_to_async
    if await sync_to_async(is_admin)(user.id):
        await _send_admin_home(update.message, first_name)
        return ConversationHandler.END

    has_phone = await sync_to_async(_has_phone)(user.id)

    if has_phone:
        await update.message.reply_text(
            f"Assalomu alaykum, <b>{first_name}</b>! 👋\n\n"
            f"🍔 <b>AslFood</b> botiga xush kelibsiz!\n\n"
            f"Mazali taomlarni tanlang va buyurtma bering 🛵",
            parse_mode="HTML",
            reply_markup=_customer_kb(),
        )
        return ConversationHandler.END

    contact_kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamimni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        f"Assalomu alaykum, <b>{first_name}</b>! 👋\n\n"
        f"🍔 <b>AslFood</b> ga xush kelibsiz!\n\n"
        f"Buyurtma berish uchun <b>telefon raqamingizni</b> ulashing.\n"
        f"Bu faqat bir marta so'raladi ✅",
        parse_mode="HTML",
        reply_markup=contact_kb,
    )
    return WAITING_PHONE


async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.contact
    user    = update.effective_user
    phone   = contact.phone_number if contact else None

    if phone and not phone.startswith("+"):
        phone = "+" + phone

    await _upsert_bot_user(user, phone=phone)

    await update.message.reply_text(
        "✅ <b>Rahmat!</b> Telefon raqamingiz saqlandi.\n\n"
        "Endi buyurtma berishingiz mumkin 🎉",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        "👇 Quyidagi tugmani bosing:",
        reply_markup=_customer_kb(),
    )
    return ConversationHandler.END


async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    first_name = update.effective_user.first_name if update.effective_user else "Mehmon"
    await update.message.reply_text(
        f"Yaxshi, {first_name}! Keyinroq ham ulashishingiz mumkin.\n"
        "Hozircha buyurtma berishingiz mumkin 👇",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        "Menyuni oching:",
        reply_markup=_customer_kb(),
    )
    return ConversationHandler.END


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _upsert_bot_user(update.effective_user)
    from asgiref.sync import sync_to_async
    if await sync_to_async(is_admin)(update.effective_user.id):
        await _send_admin_home(update.message, update.effective_user.first_name or "Admin")
        return
    await update.message.reply_text(
        "🍽️ <b>AslFood Menyu</b>",
        parse_mode="HTML",
        reply_markup=_customer_kb(),
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await _upsert_bot_user(user)
    from asgiref.sync import sync_to_async
    if not await sync_to_async(is_admin)(user.id):
        await update.message.reply_text("Bu buyruq faqat adminlar uchun.")
        return
    await _send_admin_home(update.message, user.first_name or "Admin")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Sizning Telegram ID: <code>{user.id}</code>\n\n"
        f"Admin qilish: settings.py dagi <code>TELEGRAM_ADMIN_IDS</code> ga qo'shing "
        f"yoki Django adminda BotUser → <b>is_admin</b>.",
        parse_mode="HTML",
    )


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from store.models import FoodOrder
    from asgiref.sync import sync_to_async

    user = update.effective_user
    await _upsert_bot_user(user)
    if not await sync_to_async(is_admin)(user.id):
        await update.message.reply_text("Bu buyruq faqat adminlar uchun. /admin")
        return

    active = await sync_to_async(list)(
        FoodOrder.objects.filter(
            status__in=["new", "preparing", "delivering"]
        ).order_by("created_at")[:10]
    )

    if not active:
        await update.message.reply_text("✅ Hozircha faol buyurtmalar yo'q.")
        return

    status_emoji = {
        "new":        "🟡 Yangi",
        "preparing":  "🍳 Tayyorlanmoqda",
        "delivering": "🛵 Yo'lda",
    }
    text = "📋 <b>Faol buyurtmalar:</b>\n\n"
    for o in active:
        text += (
            f"<b>#{o.order_code}</b> — {o.customer_name} ({o.phone})\n"
            f"   {status_emoji.get(o.status, o.status)} | "
            f"💰 {int(o.total_amount):,} so'm\n\n"
        )
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=_inline(admin_inline_keyboard()),
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "about":
        await query.message.reply_text(
            "🍔 <b>AslFood</b>\n\n"
            "Tez va mazali taomlar yetkazib beramiz.\n"
            "Lavash · Pizza · Gamburger · Ko'p boshqalar!\n\n"
            "📍 Manzil: ...\n"
            "📞 Tel: ...\n"
            "🕒 09:00 — 23:00",
            parse_mode="HTML",
        )

    elif data == "my_orders":
        user = query.from_user
        from store.models import FoodOrder
        from asgiref.sync import sync_to_async

        orders = await sync_to_async(list)(
            FoodOrder.objects.filter(
                telegram_id=str(user.id)
            ).order_by("-created_at")[:5]
        )

        if not orders:
            await query.message.reply_text("Sizda hali buyurtmalar yo'q.")
            return

        status_emoji = {
            "new": "🟡", "preparing": "🍳",
            "delivering": "🛵", "completed": "✅", "cancelled": "❌",
        }
        text = "📦 <b>Oxirgi buyurtmalaringiz:</b>\n\n"
        for o in orders:
            text += (
                f"{status_emoji.get(o.status,'•')} <b>#{o.order_code}</b> — "
                f"{int(o.total_amount):,} so'm\n"
                f"   {o.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            )
        await query.message.reply_text(text, parse_mode="HTML")

    elif data.startswith("ord:"):
        from store.telegram_notify import handle_group_callback
        from asgiref.sync import sync_to_async
        await sync_to_async(handle_group_callback)(query.to_dict())


async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = update.message.web_app_data.data
    await update.message.reply_text(f"✅ Ma'lumot qabul qilindi:\n{data}")


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from asgiref.sync import sync_to_async
    user = update.effective_user
    if user and await sync_to_async(is_admin)(user.id):
        await _send_admin_home(update.message, user.first_name or "Admin")
        return
    await update.message.reply_text(
        "Menyu uchun /start yoki /menu ni yuboring 👇",
        reply_markup=_customer_kb(),
    )


def create_bot_app() -> Application | None:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        return None

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_PHONE: [
                MessageHandler(filters.CONTACT, contact_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, skip_phone),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    return app


def main() -> None:
    import argparse
    import urllib.request
    import urllib.parse
    import json

    parser = argparse.ArgumentParser(description="AslFood Telegram Bot")
    parser.add_argument("--set-webhook", type=str, help="Webhook URL o'rnatish")
    parser.add_argument("--delete-webhook", action="store_true", help="Webhook o'chirish")
    parser.add_argument("--webhook-info", action="store_true", help="Webhook holati")
    args = parser.parse_args()

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ XATO: settings.py da TELEGRAM_BOT_TOKEN to'ldirilmagan!")
        sys.exit(1)

    def _tg(path: str):
        url = f"https://api.telegram.org/bot{token}/{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())

    if args.set_webhook:
        print(f"✅ Webhook: {_tg('setWebhook?url=' + urllib.parse.quote(args.set_webhook))}")
        return
    if args.delete_webhook:
        print(f"✅ O'chirildi: {_tg('deleteWebhook')}")
        return
    if args.webhook_info:
        print(json.dumps(_tg("getWebhookInfo"), indent=2, ensure_ascii=False))
        return

    if not WEBAPP_URL or "yourdomain" in WEBAPP_URL:
        print("⚠️  WEBAPP_BASE_URL to'ldirilmagan!")

    print("🤖 AslFood Bot ishga tushmoqda (polling)...")
    print(f"   Web App: {WEBAPP_URL}")
    print(f"   Guruh:   {GROUP_CHAT_ID}")

    app = create_bot_app()
    if not app:
        print("❌ Bot ilovasini yaratib bo'lmadi.")
        sys.exit(1)

    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
