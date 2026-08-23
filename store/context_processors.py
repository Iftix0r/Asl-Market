"""
AslFood global context processors.
Barcha templateda avtomatik qo'shiladi (settings.py da ro'yxatga olinadi).
"""
from store.models import Debt, FoodOrder


def panel_context(request):
    """
    Har bir sahifada sidebar uchun kerakli ma'lumotlarni qo'shadi:
    - unpaid_debts_count: to'lanmagan qarzlar soni (badge uchun)
    - new_orders_count: yangi buyurtmalar soni (badge uchun)
    """
    try:
        unpaid_debts_count = Debt.objects.filter(
            status__in=['unpaid', 'partial']
        ).count()
        new_orders_count = FoodOrder.objects.filter(status='new').count()
    except Exception:
        unpaid_debts_count = 0
        new_orders_count   = 0

    return {
        'unpaid_debts_count': unpaid_debts_count,
        'new_orders_count':   new_orders_count,
    }
