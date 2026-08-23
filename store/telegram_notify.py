"""
AslFood Telegram Notify
=======================
Guruhga va mijozlarga xabar yuboruvchi helper.
Barcha funksiyalar sinxron (urllib) — cPanel/Passenger uchun xavfsiz.
"""
import json
import logging
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Low-level helpers
# ─────────────────────────────────────────────────────────────────────────────

def _bot_token() -> str:
    from django.conf import settings
    return getattr(settings, "TELEGRAM_BOT_TOKEN", "")

def _group_id() -> str:
    from django.conf import settings
    return str(getattr(settings, "TELEGRAM_GROUP_CHAT_ID", ""))

def _api(method: str, payload: dict) -> dict:
    """Telegram Bot API ga POST so'rov yuboradi."""
    token = _bot_token()
    if not token:
        return {}
    try:
        url  = f"https://api.telegram.org/bot{token}/{method}"
        body = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Telegram API [{method}] xato: {e}")
        return {}


def _send(chat_id: str, text: str, keyboard: dict = None) -> dict:
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = keyboard
    return _api("sendMessage", payload)


def _edit(chat_id: str, message_id: int, text: str, keyboard: dict = None) -> dict:
    payload = {
        "chat_id": chat_id, "message_id": message_id,
        "text": text, "parse_mode": "HTML"
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    return _api("editMessageText", payload)


def _answer_cb(callback_id: str, text: str = "", alert: bool = False) -> None:
    _api("answerCallbackQuery", {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": alert
    })


# ─────────────────────────────────────────────────────────────────────────────
# Xabar matni va tugmalar
# ─────────────────────────────────────────────────────────────────────────────

_STATUS_EMOJI = {
    "new":        "🟡 Yangi buyurtma",
    "preparing":  "🍳 Tayyorlanmoqda",
    "delivering": "🛵 Yo'lda / Kuryerda",
    "completed":  "✅ Topshirildi",
    "cancelled":  "❌ Bekor qilindi",
}

_ORDER_TYPE = {
    "delivery": "🛵 Dostavka",
    "pickup":   "🏃 Olib ketish",
    "table":    "🍽️ Zal/Stol",
}

_PAYMENT = {
    "naqd":  "💵 Naqd pul",
    "karta": "💳 Karta/Payme/Click",
    "qarz":  "📝 QARZ",
}


def _order_text(order, title: str = "🔔 YANGI BUYURTMA") -> str:
    """Buyurtma uchun to'liq HTML xabar matni."""
    items_txt = ""
    try:
        for it in order.items.all():
            items_txt += f"  • <b>{it.quantity}×</b> {it.food_name} — {int(it.unit_price):,} so'm\n"
    except Exception:
        items_txt = "  (taomlar yuklanmadi)\n"

    addr_line    = f"📍 <b>Manzil:</b> {order.delivery_address}\n" if order.delivery_address else ""
    comment_line = f"💬 <b>Izoh:</b> {order.comment}\n"          if getattr(order, "comment", None) else ""

    # Qarz ogohlantirish — katta va ko'zga ko'rinadigan
    debt_block = ""
    if order.payment_method == "qarz":
        debt_block = (
            "┌─────────────────────────┐\n"
            "│  ⚠️  QARZGA BERILDI!   │\n"
            "└─────────────────────────┘\n"
        )

    return (
        f"{title}\n"
        f"{'─' * 32}\n"
        f"👤 <b>{order.customer_name}</b>\n"
        f"📱 {order.phone}\n"
        f"📦 {_ORDER_TYPE.get(order.order_type, order.order_type)}\n"
        f"{addr_line}"
        f"{comment_line}"
        f"{'─' * 32}\n"
        f"🍽 <b>Tarkib:</b>\n{items_txt}"
        f"{'─' * 32}\n"
        f"💰 <b>Jami:</b> {int(order.total_amount):,} so'm\n"
        f"💵 <b>To'lov:</b> {_PAYMENT.get(order.payment_method, order.payment_method)}\n"
        f"{debt_block}"
        f"📊 <b>Holat:</b> {_STATUS_EMOJI.get(order.status, order.status)}\n"
        f"🏷 <b>Kod:</b> #{order.order_code}\n"
        f"⏰ {order.created_at.strftime('%H:%M — %d.%m.%Y')}"
    )


def _order_keyboard(order_id: int, status: str) -> dict | None:
    """Status bo'yicha inline tugmalar — guruh xabari uchun."""
    rows = {
        "new": [[
            {"text": "🍳 Tayyorlashni boshlash",  "callback_data": f"ord:preparing:{order_id}"},
            {"text": "❌ Bekor qilish",             "callback_data": f"ord:cancelled:{order_id}"},
        ]],
        "preparing": [[
            {"text": "🛵 Yo'lga chiqdi",           "callback_data": f"ord:delivering:{order_id}"},
            {"text": "✅ Topshirildi (zal/pickup)", "callback_data": f"ord:completed:{order_id}"},
        ]],
        "delivering": [[
            {"text": "✅ Topshirildi — Yakunlash", "callback_data": f"ord:completed:{order_id}"},
        ]],
    }
    btns = rows.get(status)
    if not btns:
        return None
    return {"inline_keyboard": btns}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def send_order_to_group(order) -> bool:
    """
    Yangi buyurtma kelganda guruhga inline tugmali xabar yuboradi.
    Qarzga berilgan buyurtmada alohida ogohlantirish ko'rsatiladi.
    """
    gid = _group_id()
    if not gid:
        return False

    title = "🔔 <b>YANGI BUYURTMA</b>"
    if order.payment_method == "qarz":
        title = "⚠️ <b>YANGI BUYURTMA — QARZGA!</b>"

    text     = _order_text(order, title)
    keyboard = _order_keyboard(order.id, order.status)
    result   = _send(gid, text, keyboard)
    return bool(result.get("ok"))


def send_status_update_to_group(order) -> bool:
    """
    Holat paneldan o'zgartirilganda guruhga qisqa xabar.
    (Guruh inline tugmasidan emas, Django paneldan o'zgartirilsa.)
    """
    gid = _group_id()
    if not gid:
        return False
    text = (
        f"🔄 <b>#{order.order_code}</b> yangilandi\n"
        f"👤 {order.customer_name} | 📱 {order.phone}\n"
        f"📊 {_STATUS_EMOJI.get(order.status, order.status)}"
    )
    result = _send(gid, text)
    return bool(result.get("ok"))


def send_debt_reminder_to_group(debt) -> bool:
    """
    Qarzdorga eslatma — panel "Eslatma yuborish" tugmasidan chaqiriladi.
    """
    gid = _group_id()
    if not gid:
        return False
    text = (
        f"💰 <b>QARZ ESLATMASI</b>\n"
        f"{'─' * 28}\n"
        f"👤 <b>{debt.customer_name}</b>\n"
        f"📱 {debt.phone or '—'}\n"
        f"💸 Qarz: <b>{int(debt.total_amount):,} so'm</b>\n"
        f"{'✅ To\'langan: ' + str(int(debt.paid_amount)) + ' so\'m' if debt.paid_amount else ''}\n"
        f"🔴 Qoldiq: <b>{int(debt.remaining):,} so'm</b>\n"
        f"📅 Sana: {debt.created_at.strftime('%d.%m.%Y')}"
    )
    result = _send(gid, text)
    return bool(result.get("ok"))


def send_status_update_to_customer(order) -> bool:
    """Buyurtma holati o'zgarganda mijozning Telegramiga xabar."""
    chat_id = order.telegram_id
    if not chat_id and order.bot_user:
        chat_id = order.bot_user.telegram_id
    if not chat_id:
        return False

    msgs = {
        "new": (
            f"🟡 <b>Buyurtmangiz qabul qilindi!</b>\n\n"
            f"🏷 Kod: <b>#{order.order_code}</b>\n"
            f"💰 Jami: <b>{int(order.total_amount):,} so'm</b>\n"
            f"💵 To'lov: {_PAYMENT.get(order.payment_method, order.payment_method)}\n\n"
            f"Oshpazlarimiz buyurtmangizni ko'rib chiqmoqda 🍳"
        ),
        "preparing": (
            f"🍳 <b>Taomingiz tayyorlanmoqda!</b>\n\n"
            f"🏷 Kod: <b>#{order.order_code}</b>\n\n"
            f"Biroz sabr qiling, mazali taom yo'lda 😋"
        ),
        "delivering": (
            f"🛵 <b>Buyurtmangiz yo'lga chiqdi!</b>\n\n"
            f"🏷 Kod: <b>#{order.order_code}</b>\n"
            f"📍 {order.delivery_address or 'Dostavka'}\n\n"
            f"Kuryer tez yetkazib beradi! 🚀"
        ),
        "completed": (
            f"✅ <b>Buyurtma topshirildi!</b>\n\n"
            f"🏷 Kod: <b>#{order.order_code}</b>\n"
            f"💰 Jami: <b>{int(order.total_amount):,} so'm</b>\n\n"
            f"AslFood ni tanlaganingiz uchun rahmat! Yoqimli ishtaha! 🍔🍕"
        ),
        "cancelled": (
            f"🔴 <b>Buyurtmangiz bekor qilindi</b>\n\n"
            f"🏷 Kod: <b>#{order.order_code}</b>\n\n"
            f"Qo'shimcha savollar uchun biz bilan bog'laning."
        ),
    }
    text = msgs.get(order.status)
    if not text:
        return False
    result = _send(str(chat_id), text)
    return bool(result.get("ok"))


def send_debt_notification_to_customer(debt) -> bool:
    """Qarz eslatmasini to'g'ridan-to'g'ri mijozning Telegramiga yuboradi."""
    chat_id = None
    if debt.bot_user:
        chat_id = debt.bot_user.telegram_id
    elif debt.order and debt.order.telegram_id:
        chat_id = debt.order.telegram_id
    if not chat_id:
        return False

    text = (
        f"💸 <b>Qarz eslatmasi</b>\n\n"
        f"Hurmatli <b>{debt.customer_name}</b>,\n\n"
        f"Sizda AslFood da to'lanmagan qarz mavjud:\n"
        f"💰 Qarz summasi: <b>{int(debt.total_amount):,} so'm</b>\n"
        f"{'✅ To\'langan: ' + str(int(debt.paid_amount)) + ' so\'m\n' if debt.paid_amount else ''}"
        f"🔴 Qoldiq: <b>{int(debt.remaining):,} so'm</b>\n"
        f"📅 Sana: {debt.created_at.strftime('%d.%m.%Y')}\n\n"
        f"Iltimos, qarzingizni to'lang yoki biz bilan bog'laning."
    )
    result = _send(str(chat_id), text)
    return bool(result.get("ok"))


# ─────────────────────────────────────────────────────────────────────────────
# Guruh inline tugma callback handler
# ─────────────────────────────────────────────────────────────────────────────

def handle_group_callback(callback_query: dict) -> bool:
    """
    Guruhdan kelgan inline tugma bosishini qayta ishlaydi.
    callback_data formati: "ord:STATUS:ORDER_ID"
    """
    from store.models import FoodOrder

    cb_id    = callback_query.get("id", "")
    cb_data  = callback_query.get("data", "")
    message  = callback_query.get("message", {})
    chat_id  = str(message.get("chat", {}).get("id", ""))
    msg_id   = message.get("message_id")
    admin    = callback_query.get("from", {}).get("first_name", "Admin")

    # Format tekshirish
    parts = cb_data.split(":")
    if len(parts) != 3 or parts[0] != "ord":
        _answer_cb(cb_id, "Noto'g'ri format", alert=True)
        return False

    _, new_status, order_id_str = parts
    try:
        order_id = int(order_id_str)
    except ValueError:
        _answer_cb(cb_id, "Xato ID", alert=True)
        return False

    try:
        order = FoodOrder.objects.get(pk=order_id)
    except FoodOrder.DoesNotExist:
        _answer_cb(cb_id, f"#{order_id_str} buyurtma topilmadi", alert=True)
        return False

    # Holat yangilash
    order.status = new_status
    order.save(update_fields=["status"])

    # Callback javob (spinner o'chirish)
    label = _STATUS_EMOJI.get(new_status, new_status)
    _answer_cb(cb_id, f"{label} — {admin} belgiladi")

    # Guruh xabarini yangilash
    if chat_id and msg_id:
        new_text = _order_text(order, f"📋 <b>BUYURTMA #{order.order_code}</b>")
        new_kb   = _order_keyboard(order.id, new_status)
        _edit(chat_id, msg_id, new_text, new_kb)

    # Mijozga bildirishnoma
    try:
        send_status_update_to_customer(order)
    except Exception as e:
        logger.error(f"Mijozga bildirishnoma xatosi: {e}")

    return True
