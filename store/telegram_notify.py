"""
AslFood Telegram Bot — Guruhga buyurtma xabarlari yuboruvchi helper.
Django settings dan TELEGRAM_BOT_TOKEN va TELEGRAM_GROUP_CHAT_ID o'qiladi.
"""
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)


def _send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Low-level Telegram sendMessage helper (sync, no external deps)."""
    from django.conf import settings

    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_GROUP_CHAT_ID", "")

    if not bot_token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN yoki TELEGRAM_GROUP_CHAT_ID settings.py da yo'q!")
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
        logger.error(f"Telegram xabari yuborishda xato: {e}")
        return False


def send_order_to_group(order) -> bool:
    """
    Yangi buyurtma kelganda Telegram guruhga chiroyli xabar yuboradi.
    `order` — FoodOrder instance.
    """
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

    text = (
        f"🔔 <b>YANGI BUYURTMA #{order.order_code}</b>\n"
        f"{'─' * 30}\n"
        f"👤 <b>Mijoz:</b> {order.customer_name}\n"
        f"📱 <b>Telefon:</b> {order.phone}\n"
        f"📦 <b>Turi:</b> {order_type_str}\n"
        f"{address_line}"
        f"{'─' * 30}\n"
        f"🍔 <b>Buyurtma tarkibi:</b>\n"
        f"{items_text}"
        f"{'─' * 30}\n"
        f"💰 <b>Jami summa:</b> {int(order.total_amount):,} so'm\n"
        f"💵 <b>To'lov:</b> Naqd\n"
        f"⏰ <b>Vaqt:</b> {order.created_at.strftime('%H:%M, %d.%m.%Y')}"
    )

    return _send_message(text)


def send_status_update_to_group(order) -> bool:
    """
    Buyurtma holati o'zgarganda guruhga xabar yuboradi.
    """
    STATUS_EMOJI = {
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
    return _send_message(text)
