from django.db import models
from django.utils import timezone


# ==========================================================================
# ASLFOOD - FAST FOOD & RESTAURANT MODELS
# ==========================================================================

class BotUser(models.Model):
    """Telegram bot orqali ro'yxatdan o'tgan mijozlar"""
    telegram_id   = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Telegram ID")
    first_name    = models.CharField(max_length=100, blank=True, default='', verbose_name="Ismi")
    last_name     = models.CharField(max_length=100, blank=True, default='', verbose_name="Familiyasi")
    username      = models.CharField(max_length=100, blank=True, null=True, verbose_name="@username")
    phone         = models.CharField(max_length=30,  blank=True, null=True, verbose_name="Telefon raqam")
    photo_url     = models.URLField(max_length=500,  blank=True, null=True, verbose_name="Profil rasmi URL")
    language_code = models.CharField(max_length=10,  blank=True, null=True, verbose_name="Til kodi")
    is_blocked    = models.BooleanField(default=False, verbose_name="Bloklangan")
    is_admin      = models.BooleanField(default=False, verbose_name="Admin (botdan panel ochadi)")
    joined_at     = models.DateTimeField(default=timezone.now, verbose_name="Ro'yxatdan o'tgan vaqt")
    last_seen     = models.DateTimeField(default=timezone.now, verbose_name="Oxirgi faollik")
    note          = models.TextField(blank=True, null=True, verbose_name="Izoh (admin uchun)")

    class Meta:
        verbose_name = "Bot Foydalanuvchisi"
        verbose_name_plural = "Bot Foydalanuvchilari"
        ordering = ['-last_seen']

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip() or self.username or self.telegram_id
        return f"{name} (tg:{self.telegram_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username or f"ID:{self.telegram_id}"

    @property
    def total_orders(self):
        return self.orders.count()

    @property
    def total_spent(self):
        from django.db.models import Sum
        result = self.orders.filter(status='completed').aggregate(t=Sum('total_amount'))['t']
        return result or 0

    @property
    def display_phone(self):
        return self.phone or "—"

class FoodCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Taom kategoriyasi (Lavash, Pizza...)")
    slug = models.SlugField(unique=True, max_length=100, db_index=True)

    class Meta:
        verbose_name = "Taom Kategoriyasi"
        verbose_name_plural = "Taom Kategoriyalari"

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    name = models.CharField(max_length=200, verbose_name="Taom nomi")
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name="items", verbose_name="Kategoriya")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Narxi (so'm)")
    preparation_time_mins = models.IntegerField(default=15, verbose_name="Tayyorlanish vaqti (daqiqa)")
    is_available = models.BooleanField(default=True, verbose_name="Mavjud (Tugamagan)")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Rasm URL")
    ingredients = models.TextField(blank=True, null=True, verbose_name="Tarkibi / Retsept")

    class Meta:
        verbose_name = "Taom / Fast Food"
        verbose_name_plural = "Taomlar / Fast Foodlar"

    def __str__(self):
        return f"{self.name} - {self.price} so'm"


class FoodOrder(models.Model):
    ORDER_STATUS = (
        ('new', 'Yangi Buyurtma 🟡'),
        ('preparing', 'Tayyorlanmoqda 🍳'),
        ('delivering', "Yo'lda / Kuryerda 🛵"),
        ('completed', 'Topshirildi ✅'),
        ('cancelled', 'Bekor qilindi 🔴'),
    )

    ORDER_TYPES = (
        ('delivery', 'Dostavka / Yetkazib berish'),
        ('pickup', 'Olib ketish / Takeaway'),
        ('table', 'Zalda / Table Order'),
    )

    PAYMENT_METHODS = (
        ('naqd',  'Naqd pul 💵'),
        ('karta', 'Karta / Payme / Click 💳'),
        ('qarz',  'Qarz / Kredit 📝'),
    )

    order_code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Buyurtma kodi")
    customer_name = models.CharField(max_length=150, verbose_name="Mijoz ismi")
    phone = models.CharField(max_length=30, verbose_name="Telefon raqam")
    delivery_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dostavka manzili / Stol #")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Jami summa")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='naqd', verbose_name="To'lov usuli")
    is_debt_paid   = models.BooleanField(default=False, verbose_name="Qarz to'landi")
    debt_paid_at   = models.DateTimeField(null=True, blank=True, verbose_name="Qarz to'langan vaqt")
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='delivery', verbose_name="Buyurtma turi")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='new', db_index=True, verbose_name="Buyurtma holati")
    comment    = models.CharField(max_length=500, blank=True, null=True, verbose_name="Mijoz izohi")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name="Telegram ID")
    bot_user   = models.ForeignKey(
        'BotUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name="Bot foydalanuvchisi"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Buyurtma vaqti")

    class Meta:
        verbose_name = "Taom Buyurtmasi"
        verbose_name_plural = "Taom Buyurtmalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_code} - {self.customer_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Qarzga berilgan yangi buyurtma uchun avtomatik Debt yozuvi
        if is_new and self.payment_method == 'qarz':
            Debt.objects.get_or_create(
                order=self,
                defaults={
                    'bot_user':      self.bot_user,
                    'customer_name': self.customer_name,
                    'phone':         self.phone,
                    'total_amount':  self.total_amount,
                    'status':        'unpaid',
                }
            )


class Debt(models.Model):
    """Qarzga berilgan buyurtmalar / alohida qarz yozuvlari"""
    DEBT_STATUS = (
        ('unpaid',  'To\'lanmagan 🔴'),
        ('partial', 'Qisman to\'langan 🟡'),
        ('paid',    'To\'langan ✅'),
    )

    # Qarz manbayi — buyurtmadan avtomatik yoki qo'lda qo'shilgan
    order      = models.OneToOneField(
        'FoodOrder', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='debt', verbose_name="Bog'liq buyurtma"
    )
    bot_user   = models.ForeignKey(
        'BotUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='debts', verbose_name="Bot foydalanuvchisi"
    )
    # Manuel qo'shilganda (bot usersiz)
    customer_name = models.CharField(max_length=150, verbose_name="Mijoz ismi")
    phone         = models.CharField(max_length=30, blank=True, null=True, verbose_name="Telefon")

    total_amount   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Qarz summasi (so'm)")
    paid_amount    = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="To'langan summa")
    status         = models.CharField(max_length=10, choices=DEBT_STATUS, default='unpaid', db_index=True, verbose_name="Holat")
    note           = models.TextField(blank=True, null=True, verbose_name="Izoh")

    created_at     = models.DateTimeField(default=timezone.now, verbose_name="Qarz sanasi")
    due_date       = models.DateField(null=True, blank=True, verbose_name="To'lov muddati")
    paid_at        = models.DateTimeField(null=True, blank=True, verbose_name="To'langan vaqt")

    class Meta:
        verbose_name = "Qarz"
        verbose_name_plural = "Qarzdorlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} — {int(self.total_amount):,} so'm ({self.get_status_display()})"

    @property
    def remaining(self):
        return self.total_amount - self.paid_amount

    def mark_paid(self, amount=None):
        """Qarzni to'liq yoki qisman to'landi deb belgilash."""
        if amount is None or amount >= self.remaining:
            self.paid_amount = self.total_amount
            self.status = 'paid'
            self.paid_at = timezone.now()
        else:
            self.paid_amount += amount
            self.status = 'partial' if self.paid_amount > 0 else 'unpaid'
        self.save()


class FoodOrderItem(models.Model):
    order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True)
    food_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)

    @property
    def total_price(self):
        return self.quantity * self.unit_price
