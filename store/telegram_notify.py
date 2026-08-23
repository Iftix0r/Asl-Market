"""
AslFood Telegram Bot — Guruhga va mijozlarga xabarlar yuboruvchi helper.
Django settings dan TELEGRAM_BOT_TOKEN va TELEGRAM_GROUP_CHAT_ID o'qiladi.
"""
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)


def _send_message(chat_id: str, text: str, parse_mode: str = "HTML",
                  reply_markup: dict = None) -> dict:
    """Low-level Telegram sendMessage helper (sync, no external deps).
    Returns parsed JSON response dict or {} on error.
    """
    from django.conf import settings
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not bot_token or not chat_id:
        return {}
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload_data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            payload_data["reply_markup"] = reply_markup
        payload = json.dumps(payload_data).encode("utf-8")
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Telegram xabari yuborishda xato (chat_id: {chat_id}): {e}")
        return {}


def _answer_callback(callback_query_id: str, text: str = "", alert: bool = False) -> bool:
    """Telegram callback query ga javob beradi (spinner o'chiradi)."""
    from django.conf import settings
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        return False
    try:
        url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
        payload = json.dumps({
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": alert,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        logger.error(f"answerCallbackQuery xatosi: {e}")
        return False


def _edit_message_text(chat_id: str, message_id: int, text: str,
                       reply_markup: dict = None) -> bool:
    """Telegram guruhda mavjud xabar matnini tahrirlaydi."""
    from django.conf import settings
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        return False
    try:
        url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
        payload_data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            payload_data["reply_markup"] = reply_markup
        payload = json.dumps(payload_data).encode("utf-8")
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        logger.error(f"editMessageText xatosi: {e}")
        return False


def _build_order_inline_keyboard(order_id: int, current_status: str) -> dict:
    """
    Buyurtma uchun inline tugmalar (InlineKeyboardMarkup).
    Joriy statusga qarab keyingi harakatlar taklif qilinadi.
    """
    STATUS_ACTIONS = {
        'new': [
            [
                {"text": "🍳 Tayyorlash boshlandi", "callback_data": f"ord:preparing:{order_id}"},
                {"text": "❌ Bekor qilish",         "callback_data": f"ord:cancelled:{order_id}"},
            ]
        ],
        'preparing': [
            [
                {"text": "🛵 Yo'lga chiqdi",   "callback_data": f"ord:delivering:{order_id}"},
                {"text": "✅ Topshirildi",      "callback_data": f"ord:completed:{order_id}"},
            ]
        ],
        'delivering': [
            [
                {"text": "✅ Topshirildi / Yakunlash", "callback_data": f"ord:completed:{order_id}"},
            ]
        ],
    }
    buttons = STATUS_ACTIONS.get(current_status, [])
    if not buttons:
        return {}
    return {"inline_keyboard": buttons}


def _build_order_text(order) -> str:
    """Buyurtma xabar matnini shakllantiradi (qayta ishlatiladi)."""
    ORDER_TYPE_EMOJI = {
        "delivery": "🛵 Dostavka",
        "pickup":   "🏃 Olib ketish",
        "table":    "🍽️ Zal/Stol",
    }
    PAYMENT_EMOJI = {
        "naqd":  "💵 Naqd pul",
        "karta": "💳 Karta / Payme",
        "qarz":  "📝 QARZ",
    }

    order_type_str  = ORDER_TYPE_EMOJI.get(order.order_type, order.order_type)
    payment_str     = PAYMENT_EMOJI.get(order.payment_method, order.payment_method)

    items_text = ""
    try:
        for item in order.items.all():
            items_text += f"  • <b>{item.quantity}x</b> {item.food_name} — {int(item.unit_price):,} so'm\n"
    except Exception:
        items_text = "  (mahsulotlar yuklanmadi)\n"

    address_line = ""
    if order.delivery_address:
        address_line = f"📍 <b>Manzil:</b> {order.delivery_address}\n"

    comment_line = ""
    if getattr(order, 'comment', None):
        comment_line = f"💬 <b>Izoh:</b> {order.comment}\n"

    # Qarz bo'lsa katta ogohlantirish
    debt_warn = ""
    if order.payment_method == 'qarz':
        debt_warn = f"⚠️ <b>DIQQAT: BU BUYURTMA QARZGA BERILDI!</b>\n"

    STATUS_EMOJI = {
        "new":        "🟡 Yangi",
        "preparing":  "🍳 Tayyorlanmoqda",
        "delivering": "🛵 Yo'lda",
        "completed":  "✅ Topshirildi",
        "cancelled":  "❌ Bekor qilindi",
    }
    status_str = STATUS_EMOJI.get(order.status, order.status)

    return (
        f"🔔 <b>BUYURTMA #{order.order_code}</b>\n"
        f"{'─' * 30}\n"
        f"👤 <b>Mijoz:</b> {order.customer_name}\n"
        f"📱 <b>Telefon:</b> {order.phone}\n"
        f"📦 <b>Turi:</b> {order_type_str}\n"
        f"{address_line}"
        f"{comment_line}"
        f"{'─' * 30}\n"
        f"🍔 <b>Buyurtma tarkibi:</b>\n"
        f"{items_text}"
        f"{'─' * 30}\n"
        f"💰 <b>Jami summa:</b> {int(order.total_amount):,} so'm\n"
        f"💵 <b>To'lov:</b> {payment_str}\n"
        f"{debt_warn}"
        f"📊 <b>Holat:</b> {status_str}\n"
        f"⏰ <b>Vaqt:</b> {order.created_at.strftime('%H:%M, %d.%m.%Y')}"
    )


def send_order_to_group(order) -> bool:
    """
    Yangi buyurtma kelganda Telegram guruhga inline tugmali xabar yuboradi.
    """
    from django.conf import settings
    group_chat_id = getattr(settings, "TELEGRAM_GROUP_CHAT_ID", "")
    if not group_chat_id:
        return False

    text = _build_order_text(order)
    keyboard = _build_order_inline_keyboard(order.id, order.status)
    result = _send_message(group_chat_id, text, reply_markup=keyboard or None)
    return bool(result.get("ok"))


def handle_group_callback(callback_query: dict) -> bool:
    """
    Telegram guruhdan kelgan callback_query (inline tugma bosish) ni ishlatadi.
    Format: callback_data = "ord:STATUS:ORDER_ID"
    """
    from django.conf import settings
    from store.models import FoodOrder

    callback_id   = callback_query.get("id")
    callback_data = callback_query.get("data", "")
    message       = callback_query.get("message", {})
    chat_id       = str(message.get("chat", {}).get("id", ""))
    message_id    = message.get("message_id")
    from_user     = callback_query.get("from", {})
    admin_name    = from_user.get("first_name", "Admin")

    parts = callback_data.split(":")
    if len(parts) != 3 or parts[0] != "ord":
        _answer_callback(callback_id, "Noto'g'ri buyruq", alert=True)
        return False

    _, new_status, order_id_str = parts
    try:
        order_id = int(order_id_str)
    except ValueError:
        _answer_callback(callback_id, "Xato ID", alert=True)
        return False

    try:
        order = FoodOrder.objects.get(pk=order_id)
    except FoodOrder.DoesNotExist:
        _answer_callback(callback_id, f"Buyurtma #{order_id_str} topilmadi", alert=True)
        return False

    STATUS_UZ = {
        "preparing":  "🍳 Tayyorlanmoqda",
        "delivering": "🛵 Yo'lga chiqdi",
        "completed":  "✅ Topshirildi",
        "cancelled":  "❌ Bekor qilindi",
    }

    old_status = order.status
    order.status = new_status
    order.save()

    # Callback javob (spinner o'chirish)
    status_label = STATUS_UZ.get(new_status, new_status)
    _answer_callback(callback_id, f"{status_label} — {admin_name} tomonidan", alert=False)

    # Guruh xabarini yangilash (inline keyboard yangilanadi)
    if chat_id and message_id:
        new_text     = _build_order_text(order)
        new_keyboard = _build_order_inline_keyboard(order.id, new_status)
        _edit_message_text(chat_id, message_id, new_text,
                           reply_markup=new_keyboard or None)

    # Mijozga Telegram bildirishnoma
    try:
        send_status_update_to_customer(order)
    except Exception as e:
        logger.error(f"Mijozga bildirishnoma yuborishda xato: {e}")

    return True


def send_status_update_to_group(order) -> bool:
    """
    Buyurtma holati o'zgarganda guruhga qisqacha xabar yuboradi.
    (Agar holat to'g'ridan-to'g'ri paneldan o'zgartirilsa.)
    """
    from django.conf import settings
    group_chat_id = getattr(settings, "TELEGRAM_GROUP_CHAT_ID", "")
    if not group_chat_id:
        return False

    STATUS_EMOJI = {
        "new":        "🟡 Yangi buyurtma",
        "preparing":  "🍳 Tayyorlanmoqda",
        "delivering": "🛵 Kuryerda yo'lda",
        "completed":  "✅ Topshirildi",
        "cancelled":  "🔴 Bekor qilindi",
    }
    status_str = STATUS_EMOJI.get(order.status, order.status)
    text = (
        f"🔄 <b>Buyurtma #{order.order_code} yangilandi</b>\n"
        f"👤 {order.customer_name} | 📱 {order.phone}\n"
        f"📊 Holat: <b>{status_str}</b>"
    )
    result = _send_message(group_chat_id, text)
    return bool(result.get("ok"))


def send_status_update_to_customer(order) -> bool:
    """
    Buyurtma holati o'zgarganda bot orqali mijozning shaxsiy Telegramiga xabar yuboradi.
    """
    target_chat_id = order.telegram_id
    if not target_chat_id and order.bot_user:
        target_chat_id = order.bot_user.telegram_id
    if not target_chat_id:
        return False

    STATUS_MESSAGES = {
        "new": (
            f"🟡 <b>Buyurtmangiz qabul qilindi!</b>\n\n"
            f"📦 Buyurtma kodi: <b>#{order.order_code}</b>\n"
            f"💰 Jami: <b>{int(order.total_amount):,} so'm</b>\n\n"
            f"Oshxona oshpazlarimiz buyurtmangizni ko'rib chiqmoqda 🍳"
        ),
        "preparing": (
            f"🍳 <b>Buyurtmangiz tayyorlanmoqda!</b>\n\n"
            f"📦 Buyurtma kodi: <b>#{order.order_code}</b>\n\n"
            f"Oshxonamizda mazali taomingiz tayyorlanmoqda 😋"
        ),
        "delivering": (
            f"🛵 <b>Buyurtmangiz yo'lga chiqdi!</b>\n\n"
            f"📦 Buyurtma kodi: <b>#{order.order_code}</b>\n"
            f"📍 Manzil: <b>{order.delivery_address or 'Dostavka'}</b>\n\n"
            f"Kuryerimiz taomingizni tez fursatda yetkazib beradi! 🚀"
        ),
        "completed": (
            f"✅ <b>Buyurtma topshirildi!</b>\n\n"
            f"📦 Buyurtma kodi: <b>#{order.order_code}</b>\n"
            f"💰 Jami: <b>{int(order.total_amount):,} so'm</b>\n\n"
            f"AslFood ni tanlaganingiz uchun rahmat! Yoqimli ishtaha! 🍔🍕"
        ),
        "cancelled": (
            f"🔴 <b>Buyurtmangiz bekor qilindi</b>\n\n"
            f"📦 Buyurtma kodi: <b>#{order.order_code}</b>\n\n"
            f"Qo'shimcha savollaringiz bo'lsa, biz bilan bog'laning."
        ),
    }

    text = STATUS_MESSAGES.get(order.status)
    if not text:
        return False
    result = _send_message(str(target_chat_id), text)
    return bool(result.get("ok"))
