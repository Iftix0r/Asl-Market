from django.contrib import admin
from .models import FoodCategory, FoodItem, FoodOrder, FoodOrderItem


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
