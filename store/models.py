from django.db import models
from django.utils import timezone
import math

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, max_length=100, db_index=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="Kategoriya")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Sotish narxi (so'm)")
    cost_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Tan narxi (so'm)")
    stock = models.IntegerField(default=0, verbose_name="Ombor qoldig'i")
    barcode = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name="Shtrix-kod / SKU")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Rasm havolasi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def profit_per_unit(self):
        return self.price - self.cost_price

    @property
    def is_low_stock(self):
        return self.stock <= 5


class Debtor(models.Model):
    STATUS_CHOICES = (
        ('active', 'Qarzdor'),
        ('paid', "To'langan"),
    )

    name = models.CharField(max_length=150, verbose_name="F.I.SH")
    phone = models.CharField(max_length=30, db_index=True, verbose_name="Telefon raqami")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Hozirgi qarz summasi")
    initial_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Boshlang'ich qarz")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Qarz olingan sana")
    due_date = models.DateField(null=True, blank=True, verbose_name="Qaytarish muddati")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True, verbose_name="Holat")
    items_description = models.TextField(blank=True, null=True, verbose_name="Olingan buyumlar / Izoh")

    class Meta:
        verbose_name = "Qarzdor"
        verbose_name_plural = "Qarzdorlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount:,} so'm"

    @property
    def elapsed_days(self):
        """Calculates exact total days elapsed since debt creation"""
        now = timezone.now()
        delta = now - self.created_at
        return max(0, delta.days)

    @property
    def elapsed_time_str(self):
        """Calculates readable elapsed time ('X kun, Y soat o'tgan')"""
        now = timezone.now()
        delta = now - self.created_at
        total_seconds = max(0, int(delta.total_seconds()))

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        if days > 0:
            return f"{days} kun, {hours} soat o'tgan"
        elif hours > 0:
            return f"{hours} soat, {minutes} daqiqa o'tgan"
        else:
            return f"{minutes} daqiqa o'tgan"

    @property
    def overdue_level(self):
        """Returns visual overdue status: normal (<7 days), warning (7-30 days), urgent (>30 days)"""
        days = self.elapsed_days
        if days < 7:
            return 'normal'
        elif days <= 30:
            return 'warning'
        else:
            return 'urgent'


class Payment(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, related_name="payments", verbose_name="Qarzdor")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="To'langan summa")
    date = models.DateTimeField(default=timezone.now, verbose_name="To'lov vaqti")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Izoh / Usul")

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ['-date']

    def __str__(self):
        return f"{self.debtor.name} - {self.amount} so'm ({self.date.strftime('%Y-%m-%d')})"


class Sale(models.Model):
    PAYMENT_METHODS = (
        ('naqd', 'Naqd pul'),
        ('karta', 'Bank kartasi'),
        ('nasiya', 'Nasiya / Qarz'),
    )

    sale_code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Chek raqami")
    date = models.DateTimeField(default=timezone.now, verbose_name="Sotuv vaqti")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Jami summa")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='naqd', db_index=True, verbose_name="To'lov usuli")
    debtor = models.ForeignKey(Debtor, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales", verbose_name="Qarzdor (agar nasiya bo'lsa)")
    customer_name = models.CharField(max_length=150, default="Xaridor", verbose_name="Xaridor nomi")

    class Meta:
        verbose_name = "Sotuv"
        verbose_name_plural = "Sotuvlar"
        ordering = ['-date']

    def __str__(self):
        return f"Chek #{self.sale_code} - {self.total_amount} so'm"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)

    @property
    def total_price(self):
        return self.quantity * self.unit_price


# ==========================================================================
# ASLFOOD - FAST FOOD & RESTAURANT MODELS
# ==========================================================================

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
        ('delivering', 'Yo\'lda / Kuryerda 🛵'),
        ('completed', 'Topshirildi ✅'),
        ('cancelled', 'Bekor qilindi 🔴'),
    )

    ORDER_TYPES = (
        ('delivery', 'Dostavka / Yetkazib berish'),
        ('pickup', 'Olib ketish / Takeaway'),
        ('table', 'Zalda / Table Order'),
    )

    order_code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Buyurtma kodi")
    customer_name = models.CharField(max_length=150, verbose_name="Mijoz ismi")
    phone = models.CharField(max_length=30, verbose_name="Telefon raqam")
    delivery_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dostavka manzili / Stol #")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Jami summa")
    payment_method = models.CharField(max_length=20, default='naqd', verbose_name="To'lov usuli")
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='delivery', verbose_name="Buyurtma turi")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='new', db_index=True, verbose_name="Buyurtma holati")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Buyurtma vaqti")

    class Meta:
        verbose_name = "Taom Buyurtmasi"
        verbose_name_plural = "Taom Buyurtmalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_code} - {self.customer_name} ({self.get_status_display()})"


class FoodOrderItem(models.Model):
    order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True)
    food_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)

    @property
    def total_price(self):
        return self.quantity * self.unit_price
