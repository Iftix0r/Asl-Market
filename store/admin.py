from django.contrib import admin
from django.utils.html import format_html
from .models import BotUser, FoodCategory, FoodItem, FoodOrder, FoodOrderItem


class BotUserOrderInline(admin.TabularInline):
    model = FoodOrder
    extra = 0
    fields = ('order_code', 'customer_name', 'phone', 'total_amount', 'order_type', 'status', 'created_at')
    readonly_fields = fields
    can_delete = False
    show_change_link = True


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('profile_image', 'full_name', 'phone', 'username', 'telegram_id', 'is_admin', 'total_orders', 'total_spent', 'is_blocked', 'last_seen')
    list_filter = ('is_admin', 'is_blocked', 'language_code', 'joined_at', 'last_seen')
    list_editable = ('is_admin',)
    search_fields = ('first_name', 'last_name', 'username', 'phone', 'telegram_id')
    readonly_fields = ('telegram_id', 'joined_at', 'last_seen', 'total_orders', 'total_spent', 'profile_image')
    fieldsets = (
        ('Mijoz ma\'lumotlari', {
            'fields': ('profile_image', 'first_name', 'last_name', 'phone', 'photo_url', 'username', 'language_code'),
        }),
        ('Telegram va faollik', {
            'fields': ('telegram_id', 'is_admin', 'is_blocked', 'joined_at', 'last_seen'),
        }),
        ('Buyurtmalar statistikasi', {
            'fields': ('total_orders', 'total_spent'),
        }),
        ('Admin izohi', {
            'fields': ('note',),
        }),
    )
    inlines = [BotUserOrderInline]

    @admin.display(description='Profil rasmi')
    def profile_image(self, obj):
        if not obj or not obj.photo_url:
            return 'Rasm yo\'q'
        return format_html(
            '<img src="{}" width="56" height="56" style="object-fit: cover; border-radius: 50%;" />',
            obj.photo_url,
        )


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'preparation_time_mins', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'ingredients')
    list_editable = ('is_available',)


class FoodOrderItemInline(admin.TabularInline):
    model = FoodOrderItem
    extra = 0
    readonly_fields = ('food_name', 'quantity', 'unit_price')


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer_name', 'phone', 'total_amount', 'order_type', 'status', 'created_at')
    list_filter = ('status', 'order_type', 'created_at')
    search_fields = ('order_code', 'customer_name', 'phone')
    list_editable = ('status',)
    inlines = [FoodOrderItemInline]
