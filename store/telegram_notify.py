"""
AslFood Telegram Bot — Guruhga va mijozlarga xabarlar yuboruvchi helper.
Django settings dan TELEGRAM_BOT_TOKEN va TELEGRAM_GROUP_CHAT_ID o'qiladi.
"""
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)


def _send_message(chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """Low-level Telegram sendMessage helper (sync, no external deps)."""
    from django.conf import settings

    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")

    if not bot_token or not chat_id:
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        logger.error(f"Telegram xabari yuborishda xato (chat_id: {chat_id}): {e}")
        return False


def send_order_to_group(order) -> bool:
    """
    Yangi buyurtma kelganda Telegram guruhga xabar yuboradi.
    `order` — FoodOrder instance.
    """
    from django.conf import settings
    group_chat_id = getattr(settings, "TELEGRAM_GROUP_CHAT_ID", "")

    ORDER_TYPE_EMOJI = {
        "delivery": "🛵 Dostavka",
        "pickup":   "🏃 Olib ketish",
        "table":    "🍽️ Zal/Stol",
    }

    order_type_str = ORDER_TYPE_EMOJI.get(order.order_type, order.order_type)
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
    if hasattr(order, 'comment') and order.comment:
        comment_line = f"💬 <b>Izoh:</b> {order.comment}\n"

    text = (
        f"🔔 <b>YANGI BUYURTMA #{order.order_code}</b>\n"
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
        f"💵 <b>To'lov:</b> Naqd\n"
        f"⏰ <b>Vaqt:</b> {order.created_at.strftime('%H:%M, %d.%m.%Y')}"
    )

    if group_chat_id:
        _send_message(group_chat_id, text)
    return True


def send_status_update_to_group(order) -> bool:
    """
    Buyurtma holati o'zgarganda guruhga xabar yuboradi.
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
    return _send_message(group_chat_id, text)


def send_status_update_to_customer(order) -> bool:
    """
    Buyurtma holati o'zgarganda (yangi, tayyorlanmoqda, kuryerda, topshirildi, bekor qilindi)
    bot orqali mijozning shaxsiy Telegramiga xabar yuboradi.
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
            f"AslFood ni tanlaganingiz uchun rahmat! Yoqimli ishtha! 🍔🍕"
        ),
        "cancelled": (
            f"🔴 <b>Buyurtmangiz bekor qilindi</b>\n\n"
            f"📦 Buyurtma kodi: <b>#{order.order_code}</b>\n\n"
            f"Qo'shimcha savollaringiz bo'lsa, @aslfoodsupport bilan bog'laning."
        )
    }

    text = STATUS_MESSAGES.get(order.status)
    if not text:
        return False

    return _send_message(str(target_chat_id), text)
