"""
Telegram klaviatura va admin aniqlash — bot.py va webhook uchun umumiy.
"""
from django.conf import settings


def customer_webapp_url() -> str:
    return getattr(settings, "WEBAPP_BASE_URL", "").rstrip("/") + "/"


def admin_webapp_url(path: str = "") -> str:
    base = getattr(settings, "WEBAPP_BASE_URL", "").rstrip("/") + "/panel/"
    extra = (path or "").lstrip("/")
    return base + extra


def admin_id_set() -> set[str]:
    ids = getattr(settings, "TELEGRAM_ADMIN_IDS", None) or []
    result = {str(i).strip() for i in ids if str(i).strip()}
    try:
        from store.models import BotUser
        for uid in BotUser.objects.filter(is_admin=True).values_list("telegram_id", flat=True):
            if uid:
                result.add(str(uid))
    except Exception:
        pass
    return result


def is_admin(user_id) -> bool:
    if user_id is None:
        return False
    return str(user_id) in admin_id_set()


def customer_inline_keyboard() -> dict:
    url = customer_webapp_url()
    return {
        "inline_keyboard": [
            [{"text": "🍔 Menyu va Buyurtma Berish", "web_app": {"url": url}}],
            [
                {"text": "📋 Buyurtmalarim", "callback_data": "my_orders"},
                {"text": "ℹ️ Haqimizda", "callback_data": "about"},
            ],
        ]
    }


def admin_inline_keyboard() -> dict:
    panel = admin_webapp_url()
    return {
        "inline_keyboard": [
            [{"text": "🛠 Admin panel", "web_app": {"url": panel}}],
            [
                {"text": "🍳 Oshxona", "web_app": {"url": panel}},
                {"text": "📋 Buyurtmalar", "web_app": {"url": admin_webapp_url("orders/")}},
            ],
            [
                {"text": "🍔 Taomlar", "web_app": {"url": admin_webapp_url("menu/")}},
                {"text": "👥 Mijozlar", "web_app": {"url": admin_webapp_url("customers/")}},
            ],
            [{"text": "💰 Qarzdorlar", "web_app": {"url": admin_webapp_url("debts/")}}],
        ]
    }


def admin_reply_keyboard() -> dict:
    return {
        "keyboard": [[
            {"text": "🛠 Admin panel", "web_app": {"url": admin_webapp_url()}},
        ]],
        "resize_keyboard": True,
        "is_persistent": True,
    }


def admin_order_keyboard(order_id: int, status: str) -> dict:
    rows = {
        "new": [[
            {"text": "🍳 Tayyorlash", "callback_data": f"ord:preparing:{order_id}"},
            {"text": "❌ Bekor", "callback_data": f"ord:cancelled:{order_id}"},
        ]],
        "preparing": [[
            {"text": "🛵 Yo'lga chiqdi", "callback_data": f"ord:delivering:{order_id}"},
            {"text": "✅ Topshirildi", "callback_data": f"ord:completed:{order_id}"},
        ]],
        "delivering": [[
            {"text": "✅ Yakunlash", "callback_data": f"ord:completed:{order_id}"},
        ]],
    }
    keyboard = list(rows.get(status) or [])
    keyboard.append([{"text": "🛠 Panelda ochish", "web_app": {"url": admin_webapp_url()}}])
    return {"inline_keyboard": keyboard}
