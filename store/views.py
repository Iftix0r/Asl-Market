from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.db.models import Sum, F, Q, Count, DecimalField, ExpressionWrapper
from django.utils import timezone
from datetime import timedelta
import json
import uuid
import csv

from .models import (
    Category, Product, Debtor, Payment, Sale, SaleItem,
    FoodCategory, FoodItem, FoodOrder, FoodOrderItem
)


# ==========================================================================
# STOREFRONT VIEWS
# ==========================================================================

def storefront(request):
    """Public customer-facing storefront view (Supports Supermarket & Fast Food)"""
    query = request.GET.get('q', '').strip()
    cat_slug = request.GET.get('category', '').strip()
    active_tab = request.GET.get('tab', 'supermarket').strip()

    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    food_items = FoodItem.objects.select_related('category').filter(is_available=True)
    food_categories = FoodCategory.objects.all()

    if cat_slug:
        products = products.filter(category__slug=cat_slug)
        food_items = food_items.filter(category__slug=cat_slug)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(barcode__icontains=query) | Q(description__icontains=query))
        food_items = food_items.filter(Q(name__icontains=query) | Q(ingredients__icontains=query))

    context = {
        'products': products,
        'categories': categories,
        'food_items': food_items,
        'food_categories': food_categories,
        'selected_category': cat_slug,
        'active_tab': active_tab,
        'query': query
    }
    return render(request, 'storefront.html', context)


@csrf_exempt
def online_checkout_api(request):
    """AJAX Online Order Placement API Endpoint for Storefront"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            customer_name = data.get('customer_name', 'Onlayn Xaridor').strip()
            phone = data.get('phone', '').strip()

            if not cart:
                return JsonResponse({'success': False, 'error': 'Savat bo\'sh'})

            with transaction.atomic():
                total_amount = 0
                sale_items_data = []

                for item in cart:
                    prod = Product.objects.select_for_update().get(pk=item['id'])
                    qty = int(item['qty'])
                    if qty <= 0:
                        continue

                    subtotal = prod.price * qty
                    total_amount += subtotal

                    prod.stock = max(0, prod.stock - qty)
                    prod.save()

                    sale_items_data.append({
                        'product': prod,
                        'product_name': prod.name,
                        'quantity': qty,
                        'unit_price': prod.price
                    })

                code = "WEB-" + str(uuid.uuid4())[:8].upper()
                sale = Sale.objects.create(
                    sale_code=code,
                    total_amount=total_amount,
                    payment_method='naqd',
                    customer_name=f"{customer_name} ({phone})" if phone else customer_name,
                    date=timezone.now()
                )

                for item_data in sale_items_data:
                    SaleItem.objects.create(
                        sale=sale,
                        product=item_data['product'],
                        product_name=item_data['product_name'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price']
                    )

            return JsonResponse({
                'success': True,
                'sale_code': code,
                'total_amount': float(total_amount),
                'message': 'Buyurtmangiz muvaffaqiyatli qabul qilindi!'
            })

        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mahsulot topilmadi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


# ==========================================================================
# ASLFOOD KITCHEN & FAST FOOD VIEWS
# ==========================================================================

def aslfood_dashboard(request):
    """AslFood Live Kitchen Board (/aslfood/panel/)"""
    new_orders = FoodOrder.objects.filter(status='new').order_by('created_at')
    preparing_orders = FoodOrder.objects.filter(status='preparing').order_by('created_at')
    delivering_orders = FoodOrder.objects.filter(status='delivering').order_by('created_at')
    completed_orders = FoodOrder.objects.filter(status='completed').order_by('-created_at')[:15]

    total_food_sales = FoodOrder.objects.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'new_orders': new_orders,
        'preparing_orders': preparing_orders,
        'delivering_orders': delivering_orders,
        'completed_orders': completed_orders,
        'total_food_sales': total_food_sales,
    }
    return render(request, 'aslfood/dashboard.html', context)


@csrf_exempt
def aslfood_order_api(request):
    """Public Food Order Placement Endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_name = data.get('customer_name', 'Mijoz').strip()
            phone = data.get('phone', '').strip()
            delivery_address = data.get('delivery_address', 'Zalda / Takeaway').strip()
            order_type = data.get('order_type', 'delivery').strip()
            payment_method = data.get('payment_method', 'naqd').strip()
            items = data.get('items', [])

            if not items:
                return JsonResponse({'success': False, 'error': 'Savatcha bo\'sh'})

            with transaction.atomic():
                total_amount = 0
                order_code = "FD-" + str(uuid.uuid4())[:8].upper()

                order = FoodOrder.objects.create(
                    order_code=order_code,
                    customer_name=customer_name,
                    phone=phone,
                    delivery_address=delivery_address,
                    order_type=order_type,
                    payment_method=payment_method,
                    total_amount=0,
                    status='new'
                )

                for item in items:
                    food_item = get_object_or_404(FoodItem, pk=item['id'])
                    qty = int(item['qty'])
                    subtotal = food_item.price * qty
                    total_amount += subtotal

                    FoodOrderItem.objects.create(
                        order=order,
                        food_item=food_item,
                        food_name=food_item.name,
                        quantity=qty,
                        unit_price=food_item.price
                    )

                order.total_amount = total_amount
                order.save()

            return JsonResponse({
                'success': True,
                'order_code': order_code,
                'total_amount': float(total_amount),
                'message': 'Buyurtmangiz oshxonaga topshirildi!'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


@csrf_exempt
def aslfood_update_status_api(request):
    """AJAX endpoint to update order status in Live Kitchen Board"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('new_status')

            order = get_object_or_404(FoodOrder, pk=order_id)
            order.status = new_status
            order.save()

            return JsonResponse({'success': True, 'new_status': new_status, 'order_code': order.order_code})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


def aslfood_menu_list(request):
    """AslFood Menu Item Management (/aslfood/panel/menu/)"""
    food_items = FoodItem.objects.select_related('category').all()
    categories = FoodCategory.objects.all()
    context = {
        'food_items': food_items,
        'categories': categories,
    }
    return render(request, 'aslfood/menu.html', context)


def aslfood_add_item(request):
    """Add a new fast food menu item"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price', 0)
        prep_time = request.POST.get('prep_time', 15)
        image_url = request.POST.get('image_url', '').strip()
        ingredients = request.POST.get('ingredients', '').strip()

        category = FoodCategory.objects.filter(pk=category_id).first()

        if name and category and price:
            FoodItem.objects.create(
                name=name,
                category=category,
                price=price,
                preparation_time_mins=prep_time or 15,
                image_url=image_url or "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80",
                ingredients=ingredients,
                is_available=True
            )
        return redirect('aslfood_menu_list')
    return redirect('aslfood_menu_list')


@csrf_exempt
def aslfood_toggle_availability_api(request, pk):
    """One-click toggle for food availability (Mavjud/Tugagan)"""
    food_item = get_object_or_404(FoodItem, pk=pk)
    food_item.is_available = not food_item.is_available
    food_item.save()
    return JsonResponse({'success': True, 'is_available': food_item.is_available})


def aslfood_receipt_view(request, pk):
    """Printable AslFood Receipt View"""
    order = get_object_or_404(FoodOrder, pk=pk)
    context = {'order': order}
    return render(request, 'aslfood/receipt.html', context)


# ==========================================================================
# ASLMARKET RETAIL ADMIN PANEL & POS VIEWS
# ==========================================================================

def dashboard(request):
    """Main Supermarket Admin Dashboard (/panel/)"""
    total_sales_count = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_debtors = Debtor.objects.filter(status='active').count()
    total_debt_amount = Debtor.objects.filter(status='active').aggregate(total=Sum('amount'))['total'] or 0

    urgent_debtors = Debtor.objects.filter(status='active').order_by('created_at')[:5]
    recent_sales = Sale.objects.select_related('debtor').all()[:7]
    low_stock_products = Product.objects.filter(stock__lte=5)[:5]

    context = {
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'total_debtors': total_debtors,
        'total_debt_amount': total_debt_amount,
        'urgent_debtors': urgent_debtors,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'panel/dashboard.html', context)


def analytics_view(request):
    """Analytics & Sales Charts (/panel/analytics/)"""
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)

    daily_sales = Sale.objects.filter(date__date__gte=seven_days_ago) \
        .values('date__date') \
        .annotate(total=Sum('total_amount'), count=Count('id')) \
        .order_by('date__date')

    sales_by_payment = Sale.objects.values('payment_method') \
        .annotate(total=Sum('total_amount'))

    top_products = SaleItem.objects.values('product_name') \
        .annotate(total_qty=Sum('quantity'), total_sum=Sum(F('quantity') * F('unit_price'))) \
        .order_by('-total_qty')[:5]

    context = {
        'daily_sales': list(daily_sales),
        'sales_by_payment': list(sales_by_payment),
        'top_products': list(top_products),
    }
    return render(request, 'panel/analytics.html', context)


def products_list(request):
    """Products Catalog Management (/panel/products/)"""
    query = request.GET.get('q', '').strip()
    cat_id = request.GET.get('category', '')
    low_stock_only = request.GET.get('low_stock', '')

    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    if cat_id:
        products = products.filter(category_id=cat_id)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    if low_stock_only == '1':
        products = products.filter(stock__lte=5)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': cat_id,
        'low_stock_only': low_stock_only,
    }
    return render(request, 'panel/products.html', context)


def add_product(request):
    """Add a new retail product"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price', 0)
        cost_price = request.POST.get('cost_price', 0)
        stock = request.POST.get('stock', 0)
        barcode = request.POST.get('barcode', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        description = request.POST.get('description', '').strip()

        category = Category.objects.filter(pk=category_id).first()

        if name and price:
            Product.objects.create(
                name=name,
                category=category,
                price=price,
                cost_price=cost_price or 0,
                stock=stock or 0,
                barcode=barcode or None,
                image_url=image_url or None,
                description=description or None
            )
        return redirect('products_list')
    return redirect('products_list')


def edit_product(request, pk):
    """Edit existing product details"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name).strip()
        category_id = request.POST.get('category')
        product.category = Category.objects.filter(pk=category_id).first()
        product.price = request.POST.get('price', product.price)
        product.cost_price = request.POST.get('cost_price', product.cost_price)
        product.stock = request.POST.get('stock', product.stock)
        product.barcode = request.POST.get('barcode', product.barcode)
        product.image_url = request.POST.get('image_url', product.image_url)
        product.description = request.POST.get('description', product.description)
        product.save()
        return redirect('products_list')
    return redirect('products_list')


def delete_product(request, pk):
    """Delete product from database"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('products_list')
    return redirect('products_list')


# ==========================================================================
# DEBTORS (QARZDORLAR) MODULE
# ==========================================================================

def debtors_list(request):
    """Debtors List & Credit Management (/panel/debtors/)"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'active').strip()

    debtors = Debtor.objects.all()
    if status_filter:
        debtors = debtors.filter(status=status_filter)
    if query:
        debtors = debtors.filter(Q(name__icontains=query) | Q(phone__icontains=query))

    total_active_debt = Debtor.objects.filter(status='active').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'debtors': debtors,
        'query': query,
        'status_filter': status_filter,
        'total_active_debt': total_active_debt,
    }
    return render(request, 'panel/debtors.html', context)


def add_debtor(request):
    """Add a new debtor manually"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        amount = request.POST.get('amount', 0)
        due_date = request.POST.get('due_date', None)
        items_description = request.POST.get('items_description', '').strip()

        if name and phone and amount:
            Debtor.objects.create(
                name=name,
                phone=phone,
                amount=amount,
                initial_amount=amount,
                due_date=due_date if due_date else None,
                items_description=items_description,
                status='active'
            )
        return redirect('debtors_list')
    return redirect('debtors_list')


@csrf_exempt
def pay_debt(request):
    """Record a debt payment from a debtor"""
    if request.method == 'POST':
        debtor_id = request.POST.get('debtor_id') or json.loads(request.body or '{}').get('debtor_id')
        pay_amount = request.POST.get('amount') or json.loads(request.body or '{}').get('amount')
        note = request.POST.get('note', "To'lov").strip() or "To'lov"

        if debtor_id and pay_amount:
            try:
                with transaction.atomic():
                    debtor = Debtor.objects.select_for_update().get(pk=debtor_id)
                    pay_val = float(pay_amount)

                    payment = Payment.objects.create(
                        debtor=debtor,
                        amount=pay_val,
                        note=note,
                        date=timezone.now()
                    )

                    debtor.amount = max(0, debtor.amount - pay_val)
                    if debtor.amount == 0:
                        debtor.status = 'paid'
                    debtor.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({'success': True, 'remaining_amount': float(debtor.amount), 'status': debtor.status})

                return redirect('debtors_list')
            except Exception as e:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'error': str(e)})

    return redirect('debtors_list')


def search_debtors_api(request):
    """Live search API for debtors (Used in POS Nasiya selector)"""
    query = request.GET.get('q', '').strip()
    debtors = Debtor.objects.filter(status='active')
    if query:
        debtors = debtors.filter(Q(name__icontains=query) | Q(phone__icontains=query))

    results = []
    for d in debtors[:15]:
        results.append({
            'id': d.id,
            'name': d.name,
            'phone': d.phone,
            'amount': float(d.amount),
        })
    return JsonResponse({'success': True, 'debtors': results})


def debtor_history_api(request, pk):
    """Fetch payment and purchase history for a debtor"""
    debtor = get_object_or_404(Debtor, pk=pk)
    payments = debtor.payments.all()
    sales = debtor.sales.all()

    payment_list = [{'amount': float(p.amount), 'date': p.date.strftime('%Y-%m-%d %H:%M'), 'note': p.note} for p in payments]
    sale_list = [{'code': s.sale_code, 'amount': float(s.total_amount), 'date': s.date.strftime('%Y-%m-%d %H:%M')} for s in sales]

    return JsonResponse({
        'success': True,
        'debtor': {
            'name': debtor.name,
            'phone': debtor.phone,
            'amount': float(debtor.amount),
            'initial_amount': float(debtor.initial_amount),
            'elapsed_str': debtor.elapsed_time_str,
            'overdue_level': debtor.overdue_level,
            'created_at': debtor.created_at.strftime('%Y-%m-%d')
        },
        'payments': payment_list,
        'sales': sale_list
    })


def debt_receipt_view(request, pk):
    """Printable Debt Receipt View"""
    debtor = get_object_or_404(Debtor, pk=pk)
    latest_payment = debtor.payments.first()
    context = {
        'debtor': debtor,
        'latest_payment': latest_payment
    }
    return render(request, 'aslfood/receipt.html', context)


def export_debtors_csv(request):
    """Export Debtors list to CSV file"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="qarzdorlar_royxati.csv"'

    writer = csv.writer(response)
    writer.writerow(['F.I.SH', 'Telefon', 'Boshlang\'ich qarz', 'Hozirgi qarz', 'Qarz olingan vaqt', 'Qaytarish muddati', 'Holat', 'Izoh'])

    debtors = Debtor.objects.all().order_by('-amount')
    for d in debtors:
        writer.writerow([
            d.name,
            d.phone,
            d.initial_amount,
            d.amount,
            d.created_at.strftime('%Y-%m-%d %H:%M'),
            d.due_date.strftime('%Y-%m-%d') if d.due_date else 'Belgilanmagan',
            d.get_status_display(),
            d.items_description or ''
        ])
    return response


# ==========================================================================
# POS KASSA MODULE
# ==========================================================================

def pos_view(request):
    """POS Cashier Terminal Interface (/panel/pos/)"""
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()
    debtors = Debtor.objects.filter(status='active')

    context = {
        'categories': categories,
        'products': products,
        'debtors': debtors,
    }
    return render(request, 'panel/pos.html', context)


def pos_scan_barcode_api(request):
    """Barcode Scanner Quick Lookup API Endpoint"""
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return JsonResponse({'success': False, 'error': 'Shtrix-kod kiritilmadi'})

    product = Product.objects.filter(barcode=barcode).first()
    if not product:
        # Search by exact name fallback
        product = Product.objects.filter(name__iexact=barcode).first()

    if product:
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'stock': product.stock,
                'barcode': product.barcode,
                'image_url': product.image_url
            }
        })
    return JsonResponse({'success': False, 'error': 'Mahsulot topilmadi'})


@csrf_exempt
def pos_checkout_api(request):
    """POS Cashier Checkout API Endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            payment_method = data.get('payment_method', 'naqd')
            debtor_id = data.get('debtor_id')
            new_debtor_name = data.get('new_debtor_name', '').strip()
            new_debtor_phone = data.get('new_debtor_phone', '').strip()

            if not cart:
                return JsonResponse({'success': False, 'error': 'Savat bo\'sh!'})

            with transaction.atomic():
                total_amount = 0
                sale_items_data = []

                for item in cart:
                    prod = Product.objects.select_for_update().get(pk=item['id'])
                    qty = int(item['qty'])
                    if qty <= 0:
                        continue

                    subtotal = prod.price * qty
                    total_amount += subtotal

                    prod.stock = max(0, prod.stock - qty)
                    prod.save()

                    sale_items_data.append({
                        'product': prod,
                        'product_name': prod.name,
                        'quantity': qty,
                        'unit_price': prod.price
                    })

                sale_code = "POS-" + str(uuid.uuid4())[:8].upper()
                debtor_obj = None
                customer_name = "Kassa Xaridori"

                # Handle Nasiya (Credit)
                if payment_method == 'nasiya':
                    if debtor_id:
                        debtor_obj = Debtor.objects.select_for_update().get(pk=debtor_id)
                        debtor_obj.amount += total_amount
                        debtor_obj.save()
                        customer_name = debtor_obj.name
                    elif new_debtor_name and new_debtor_phone:
                        debtor_obj = Debtor.objects.create(
                            name=new_debtor_name,
                            phone=new_debtor_phone,
                            amount=total_amount,
                            initial_amount=total_amount,
                            status='active'
                        )
                        customer_name = new_debtor_name
                    else:
                        return JsonResponse({'success': False, 'error': 'Nasiya uchun qarzdor tanlanmadi yoki yangi kiritilmadi!'})

                sale = Sale.objects.create(
                    sale_code=sale_code,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    debtor=debtor_obj,
                    customer_name=customer_name,
                    date=timezone.now()
                )

                for item_data in sale_items_data:
                    SaleItem.objects.create(
                        sale=sale,
                        product=item_data['product'],
                        product_name=item_data['product_name'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price']
                    )

            return JsonResponse({
                'success': True,
                'sale_code': sale_code,
                'total_amount': float(total_amount),
                'payment_method': payment_method,
                'customer_name': customer_name,
                'date': sale.date.strftime('%Y-%m-%d %H:%M'),
                'items': [{'name': i['product_name'], 'qty': i['quantity'], 'price': float(i['unit_price']), 'subtotal': float(i['quantity'] * i['unit_price'])} for i in sale_items_data]
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


# ==========================================================================
# SALES HISTORY & EXPORTS
# ==========================================================================

def sales_history(request):
    """Sales Log History (/panel/sales/)"""
    query = request.GET.get('q', '').strip()
    payment_method = request.GET.get('payment_method', '').strip()

    sales = Sale.objects.select_related('debtor').prefetch_related('items').all()
    if payment_method:
        sales = sales.filter(payment_method=payment_method)
    if query:
        sales = sales.filter(Q(sale_code__icontains=query) | Q(customer_name__icontains=query))

    context = {
        'sales': sales,
        'query': query,
        'selected_payment': payment_method,
    }
    return render(request, 'panel/sales.html', context)


def export_sales_csv(request):
    """Export Sales log to CSV file"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sotuvlar_tarixi.csv"'

    writer = csv.writer(response)
    writer.writerow(['Chek kodi', 'Xaridor', 'Jami summa (so\'m)', 'To\'lov usuli', 'Sotuv vaqti'])

    sales = Sale.objects.all().order_by('-date')
    for s in sales:
        writer.writerow([
            s.sale_code,
            s.customer_name,
            s.total_amount,
            s.get_payment_method_display(),
            s.date.strftime('%Y-%m-%d %H:%M')
        ])
    return response


# ==========================================================================
# DEMO DATA SEEDERS
# ==========================================================================

def seed_demo_data(request):
    """Seed comprehensive retail mock data into SQLite database"""
    with transaction.atomic():
        # Supermarket Categories
        c1, _ = Category.objects.get_or_create(slug="ichimliklar", defaults={'name': "Ichimliklar & Sharbating"})
        c2, _ = Category.objects.get_or_create(slug="sut-mahsulotlari", defaults={'name': "Sut va Qatiq Mahsulotlari"})
        c3, _ = Category.objects.get_or_create(slug="shirinliklar", defaults={'name': "Shirinliklar va Pecheynelar"})
        c4, _ = Category.objects.get_or_create(slug="yormolar", defaults={'name': "Yorma va Makaronlar"})

        # Supermarket Products
        products_data = [
            ("Coca-Cola 1.5L", c1, 14000, 11000, 45, "478000001001", "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=400&q=80"),
            ("Pepsi 1.0L", c1, 11000, 8500, 30, "478000001002", "https://images.unsplash.com/photo-1554866585-cd94860890b7?auto=format&fit=crop&w=400&q=80"),
            ("Mussaffo Sut 3.2%", c2, 16000, 13000, 3, "478000002001", "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80"),
            ("President Sariyog' 200g", c2, 38000, 31000, 12, "478000002002", "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=400&q=80"),
            ("Nestle Shokolad 90g", c3, 15000, 11500, 25, "478000003001", "https://images.unsplash.com/photo-1582176647444-301594957597?auto=format&fit=crop&w=400&q=80"),
            ("Lays Chips 140g", c3, 19000, 14500, 4, "478000003002", "https://images.unsplash.com/photo-1566478989037-eec170784d0b?auto=format&fit=crop&w=400&q=80"),
            ("Makaron Shells 500g", c4, 9000, 6800, 60, "478000004001", "https://images.unsplash.com/photo-1621996346565-e3d5d6281282?auto=format&fit=crop&w=400&q=80"),
        ]

        for p_name, cat, price, cost, stock, barcode, img in products_data:
            Product.objects.get_or_create(
                barcode=barcode,
                defaults={
                    'name': p_name,
                    'category': cat,
                    'price': price,
                    'cost_price': cost,
                    'stock': stock,
                    'image_url': img
                }
            )

        # Mock Debtors
        now = timezone.now()
        Debtor.objects.get_or_create(
            phone="+998901234567",
            defaults={
                'name': "Jasur Aliyev",
                'amount': 350000,
                'initial_amount': 500000,
                'created_at': now - timedelta(days=3),
                'items_description': "Kola, chips va sariyog'"
            }
        )
        Debtor.objects.get_or_create(
            phone="+998939876543",
            defaults={
                'name': "Sardor Karimov",
                'amount': 820000,
                'initial_amount': 820000,
                'created_at': now - timedelta(days=14),
                'items_description': "Sut va makaronlar (Xaftalik bozor)"
            }
        )
        Debtor.objects.get_or_create(
            phone="+998991112233",
            defaults={
                'name': "Otabek Qosimov",
                'amount': 1450000,
                'initial_amount': 1450000,
                'created_at': now - timedelta(days=45),
                'items_description': "Katta haajmdagi oziq-ovqat mahsulotlari"
            }
        )

    return HttpResponse("AslMarket Supermarket Demo Ma'lumotlari omborga kiritildi! <a href='/panel/'>Dashboard ga qaytish</a>")


def aslfood_seed_data(request):
    """Seed Fast-Food mock data into SQLite database"""
    with transaction.atomic():
        fc1, _ = FoodCategory.objects.get_or_create(slug="lavash-burger", defaults={'name': "Lavash va Burgerlar"})
        fc2, _ = FoodCategory.objects.get_or_create(slug="pizza-pide", defaults={'name': "Pizza va Pide"})
        fc3, _ = FoodCategory.objects.get_or_create(slug="fast-ichimliklar", defaults={'name': "Ichimliklar va Kokteyllar"})
        fc4, _ = FoodCategory.objects.get_or_create(slug="gamburgerlar", defaults={'name': "Souslar va Gamburgerlar"})

        food_data = [
            ("Mol go'shtli Lavash Big", fc1, 35000, 15, "https://images.unsplash.com/photo-1561758033-d89a9ad46330?auto=format&fit=crop&w=400&q=80", "Mol go'shti, poytaxt sous, pomidor, bodring, chipslar"),
            ("Tovuqli Cheese Lavash", fc1, 32000, 12, "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?auto=format&fit=crop&w=400&q=80", "Tovuq go'shti, pishloq, bodring, maxsus mayo-sous"),
            ("Pepperoni Pizza 32sm", fc2, 75000, 20, "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?auto=format&fit=crop&w=400&q=80", "Mozzarella, Pepperoni kolbasa, tomat sous, oregano"),
            ("Margarita Pizza 30sm", fc2, 65000, 18, "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=400&q=80", "Mozzarella pishlog'i, yangi pomidorlar, bazilik"),
            ("Double Beef Cheeseburger", fc4, 42000, 10, "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=400&q=80", "2x Mol go'shti kotleti, double Cheddar pishlog'i, poytaxt sous"),
            ("Mojito Limonade 0.5L", fc3, 18000, 5, "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=400&q=80", "Yalpiz, laym, gazlangan suv, muz"),
        ]

        for f_name, cat, price, prep, img, ing in food_data:
            FoodItem.objects.get_or_create(
                name=f_name,
                defaults={
                    'category': cat,
                    'price': price,
                    'preparation_time_mins': prep,
                    'image_url': img,
                    'ingredients': ing,
                    'is_available': True
                }
            )

        # Mock Kitchen Orders
        if FoodOrder.objects.count() == 0:
            item_lavash = FoodItem.objects.filter(name__icontains="Lavash").first()
            item_pizza = FoodItem.objects.filter(name__icontains="Pizza").first()

            o1 = FoodOrder.objects.create(
                order_code="FD-8812A",
                customer_name="Dilshod Rahimov",
                phone="+998974443322",
                delivery_address="Navoiy ko'chasi 14-uy",
                total_amount=110000,
                order_type="delivery",
                status="new"
            )
            if item_lavash and item_pizza:
                FoodOrderItem.objects.create(order=o1, food_item=item_lavash, food_name=item_lavash.name, quantity=1, unit_price=item_lavash.price)
                FoodOrderItem.objects.create(order=o1, food_item=item_pizza, food_name=item_pizza.name, quantity=1, unit_price=item_pizza.price)

            o2 = FoodOrder.objects.create(
                order_code="FD-4401B",
                customer_name="Alisher aka (Stol #4)",
                phone="+998901110099",
                delivery_address="Stol #4",
                total_amount=42000,
                order_type="table",
                status="preparing"
            )

    return HttpResponse("AslFood Fast-Food Demo Ma'lumotlari kiritildi! <a href='/aslfood/panel/'>Oshxona Paneliga o'tish</a>")


# ==========================================================================
# ASLFOOD MOBILE APP REST API ENDPOINTS
# ==========================================================================

def api_food_menu(request):
    """GET /api/food/menu/ — Get list of available food menu items"""
    cat_slug = request.GET.get('category', '')
    query = request.GET.get('q', '')

    items = FoodItem.objects.filter(is_available=True).select_related('category')
    if cat_slug:
        items = items.filter(category__slug=cat_slug)
    if query:
        items = items.filter(Q(name__icontains=query) | Q(ingredients__icontains=query))

    data = []
    for item in items:
        data.append({
            'id': item.id,
            'name': item.name,
            'category': item.category.name if item.category else '',
            'category_slug': item.category.slug if item.category else '',
            'price': float(item.price),
            'prep_time': item.preparation_time_mins,
            'image_url': item.image_url,
            'ingredients': item.ingredients
        })
    return JsonResponse({'success': True, 'count': len(data), 'menu': data})


def api_food_menu_all(request):
    """GET /api/food/menu/all/ — Admin all menu items including unavailable"""
    items = FoodItem.objects.select_related('category').all()
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'name': item.name,
            'category': item.category.name if item.category else '',
            'price': float(item.price),
            'is_available': item.is_available,
            'image_url': item.image_url
        })
    return JsonResponse({'success': True, 'menu': data})


@csrf_exempt
def api_food_add_item(request):
    """POST /api/food/menu/add/ — Add menu item via API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category = FoodCategory.objects.filter(pk=data.get('category_id')).first()
            item = FoodItem.objects.create(
                name=data.get('name'),
                category=category,
                price=data.get('price'),
                preparation_time_mins=data.get('prep_time', 15),
                image_url=data.get('image_url', ''),
                ingredients=data.get('ingredients', ''),
                is_available=True
            )
            return JsonResponse({'success': True, 'id': item.id, 'name': item.name})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST talab qilinadi'})


@csrf_exempt
def api_food_edit_item(request, pk):
    """POST /api/food/menu/edit/<id>/ — Edit menu item via API"""
    if request.method == 'POST':
        try:
            item = get_object_or_404(FoodItem, pk=pk)
            data = json.loads(request.body)
            item.name = data.get('name', item.name)
            item.price = data.get('price', item.price)
            if 'category_id' in data:
                item.category = FoodCategory.objects.filter(pk=data['category_id']).first()
            item.save()
            return JsonResponse({'success': True, 'id': item.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST talab qilinadi'})


@csrf_exempt
def api_food_delete_item(request, pk):
    """POST /api/food/menu/delete/<id>/ — Delete menu item via API"""
    if request.method == 'POST':
        item = get_object_or_404(FoodItem, pk=pk)
        item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'POST talab qilinadi'})


@csrf_exempt
def api_food_toggle(request, pk):
    """POST /api/food/menu/toggle/<id>/ — Toggle item availability"""
    item = get_object_or_404(FoodItem, pk=pk)
    item.is_available = not item.is_available
    item.save()
    return JsonResponse({'success': True, 'is_available': item.is_available})


def api_food_categories(request):
    """GET /api/food/categories/ — Get all food categories"""
    categories = FoodCategory.objects.all()
    data = [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in categories]
    return JsonResponse({'success': True, 'categories': data})


def api_food_orders(request):
    """GET /api/food/orders/ — Get list of food orders"""
    status_filter = request.GET.get('status', '')
    orders = FoodOrder.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)

    data = []
    for o in orders[:30]:
        data.append({
            'id': o.id,
            'order_code': o.order_code,
            'customer_name': o.customer_name,
            'phone': o.phone,
            'delivery_address': o.delivery_address,
            'total_amount': float(o.total_amount),
            'order_type': o.order_type,
            'status': o.status,
            'status_display': o.get_status_display(),
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'success': True, 'orders': data})


@csrf_exempt
def api_food_place_order(request):
    """POST /api/food/orders/place/ — Mobile App place order endpoint"""
    return aslfood_order_api(request)


@csrf_exempt
def api_food_order_status_update(request):
    """POST /api/food/orders/status/ — Update order status via API"""
    return aslfood_update_status_api(request)


def api_food_order_detail(request, pk):
    """GET /api/food/orders/<id>/ — Order detail endpoint"""
    order = get_object_or_404(FoodOrder, pk=pk)
    items = order.items.all()
    item_data = [{'name': i.food_name, 'qty': i.quantity, 'price': float(i.unit_price), 'total': float(i.total_price)} for i in items]

    return JsonResponse({
        'success': True,
        'order': {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'phone': order.phone,
            'delivery_address': order.delivery_address,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'items': item_data
        }
    })


def api_food_order_by_code(request, code):
    """GET /api/food/orders/track/<code>/ — Track order by code"""
    order = FoodOrder.objects.filter(order_code=code.upper()).first()
    if not order:
        return JsonResponse({'success': False, 'error': 'Buyurtma topilmadi'})

    items = order.items.all()
    item_data = [{'name': i.food_name, 'qty': i.quantity, 'price': float(i.unit_price), 'total': float(i.total_price)} for i in items]

    return JsonResponse({
        'success': True,
        'order': {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'items': item_data
        }
    })


def api_food_stats(request):
    """GET /api/food/stats/ — Get basic fast food analytics"""
    completed_orders = FoodOrder.objects.filter(status='completed')
    total_revenue = completed_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    active_orders_count = FoodOrder.objects.filter(status__in=['new', 'preparing', 'delivering']).count()

    return JsonResponse({
        'success': True,
        'stats': {
            'total_revenue': float(total_revenue),
            'completed_orders_count': completed_orders.count(),
            'active_orders_count': active_orders_count
        }
    })


# ==========================================================================
# SHIFT SUMMARY & TELEGRAM NOTIFICATION HELPERS
# ==========================================================================

def shift_summary_api(request):
    """GET /panel/shift-summary/ — Cashier shift sales report"""
    today = timezone.now().date()
    today_sales = Sale.objects.filter(date__date=today)

    total_naqd = today_sales.filter(payment_method='naqd').aggregate(t=Sum('total_amount'))['t'] or 0
    total_karta = today_sales.filter(payment_method='karta').aggregate(t=Sum('total_amount'))['t'] or 0
    total_nasiya = today_sales.filter(payment_method='nasiya').aggregate(t=Sum('total_amount'))['t'] or 0
    grand_total = today_sales.aggregate(t=Sum('total_amount'))['t'] or 0

    return JsonResponse({
        'success': True,
        'date': today.strftime('%Y-%m-%d'),
        'sales_count': today_sales.count(),
        'total_naqd': float(total_naqd),
        'total_karta': float(total_karta),
        'total_nasiya': float(total_nasiya),
        'grand_total': float(grand_total)
    })


def send_telegram_notification(text):
    """Optional Helper to dispatch instant Telegram alert on new orders"""
    import urllib.request
    import urllib.parse
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if bot_token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            params = urllib.parse.urlencode({'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}).encode('utf-8')
            req = urllib.request.Request(url, data=params)
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass

