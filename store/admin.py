from django.contrib import admin
from .models import Category, Product, Debtor, Payment, Sale, SaleItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'cost_price', 'stock', 'barcode')
    list_filter = ('category',)
    search_fields = ('name', 'barcode')

@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'amount', 'created_at', 'elapsed_time_str', 'status', 'overdue_level')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('debtor', 'amount', 'date', 'note')
    list_filter = ('date',)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_code', 'customer_name', 'total_amount', 'payment_method', 'date')
    list_filter = ('payment_method', 'date')
    inlines = [SaleItemInline]
