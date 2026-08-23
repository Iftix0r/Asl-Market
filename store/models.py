from django.db import models
from django.utils import timezone


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
        ('delivering', "Yo'lda / Kuryerda 🛵"),
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
    comment = models.CharField(max_length=500, blank=True, null=True, verbose_name="Mijoz izohi")
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
