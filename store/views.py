from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import uuid
import csv

from .models import Category, Product, Debtor, Payment, Sale, SaleItem, FoodCategory, FoodItem, FoodOrder, FoodOrderItem


def storefront(request):
    """Public customer-facing storefront view (Supports both Supermarket and Fast-Food tabs)"""
    query = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    active_tab = request.GET.get('tab', 'supermarket')

    products = Product.objects.all()
    categories = Category.objects.all()

    food_items = FoodItem.objects.filter(is_available=True)
    food_categories = FoodCategory.objects.all()

    if cat_slug:
        products = products.filter(category__slug=cat_slug)
        food_items = food_items.filter(category__slug=cat_slug)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
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
            customer_name = data.get('customer_name', 'Onlayn Xaridor')
            phone = data.get('phone', '')

            if not cart:
                return JsonResponse({'success': False, 'error': 'Savat bo\'sh'})

            total_amount = 0
            sale_items_data = []

            for item in cart:
                prod = Product.objects.get(pk=item['id'])
                qty = int(item['qty'])
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
                customer_name=f"{customer_name} ({phone})",
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

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


# ==========================================================================
# ASLFOOD VIEWS & APIS (/aslfood/panel/)
# ==========================================================================

def aslfood_dashboard(request):
    """AslFood Live Kitchen Board (/aslfood/panel/)"""
    new_orders = FoodOrder.objects.filter(status='new').order_by('created_at')
    preparing_orders = FoodOrder.objects.filter(status='preparing').order_by('created_at')
    delivering_orders = FoodOrder.objects.filter(status='delivering').order_by('created_at')
    completed_orders = FoodOrder.objects.filter(status='completed').order_by('-created_at')[:10]

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

            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


def aslfood_menu_list(request):
    """AslFood Menu Item Management (/aslfood/panel/menu/)"""
    food_items = FoodItem.objects.all()
    categories = FoodCategory.objects.all()
    context = {
        'food_items': food_items,
        'categories': categories,
    }
    return render(request, 'aslfood/menu.html', context)


def aslfood_add_item(request):
    """Add a new fast food menu item"""
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        prep_time = request.POST.get('prep_time', 15)
        image_url = request.POST.get('image_url', '')
        ingredients = request.POST.get('ingredients', '')

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


@csrf_exempt
def aslfood_order_api(request):
    """Storefront Fast Food Order API Endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            customer_name = data.get('customer_name', 'Mijoz')
            phone = data.get('phone', '')
            address = data.get('address', '')
            order_type = data.get('order_type', 'delivery')

            if not cart:
                return JsonResponse({'success': False, 'error': 'Taomlar savati bo\'sh'})

            total_amount = 0
            order_items = []

            for item in cart:
                food = FoodItem.objects.get(pk=item['id'])
                qty = int(item['qty'])
                subtotal = food.price * qty
                total_amount += subtotal

                order_items.append({
                    'food': food,
                    'name': food.name,
                    'qty': qty,
                    'price': food.price
                })

            code = "FOOD-" + str(uuid.uuid4())[:6].upper()
            order = FoodOrder.objects.create(
                order_code=code,
                customer_name=customer_name,
                phone=phone,
                delivery_address=address,
                total_amount=total_amount,
                order_type=order_type,
                status='new',
                created_at=timezone.now()
            )

            for item in order_items:
                FoodOrderItem.objects.create(
                    order=order,
                    food_item=item['food'],
                    food_name=item['name'],
                    quantity=item['qty'],
                    unit_price=item['price']
                )

            return JsonResponse({
                'success': True,
                'order_code': code,
                'total_amount': float(total_amount),
                'message': 'Taom buyurtmangiz qabul qilindi! Oshpaz tayyorlamoqda 🍳'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


def aslfood_seed_data(request):
    """Seeds initial Uzbek fast food items into database"""
    cat_lavash, _ = FoodCategory.objects.get_or_create(name="Lavashlar", slug="lavashlar")
    cat_burger, _ = FoodCategory.objects.get_or_create(name="Gamburger va Chizburger", slug="gamburgerlar")
    cat_pizza, _ = FoodCategory.objects.get_or_create(name="Pizzalar", slug="pizzalar")
    cat_drink, _ = FoodCategory.objects.get_or_create(name="Ichimliklar & Shirinliklar", slug="ichimliklar")

    if FoodItem.objects.count() == 0:
        FoodItem.objects.create(
            name="Asl Beef Lavash Mini/Big",
            category=cat_lavash,
            price=32000,
            preparation_time_mins=10,
            image_url="https://images.unsplash.com/photo-1561758033-d89a9ad46330?auto=format&fit=crop&w=600&q=80",
            ingredients="Mol go'shti, pishloq, chips, pomidor, sous, ingichka xamir",
            is_available=True
        )

        FoodItem.objects.create(
            name="Double Cheeseburger Supreme",
            category=cat_burger,
            price=38000,
            preparation_time_mins=12,
            image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80",
            ingredients="Ikkita shira kotleta, eritilgan Chedder pishlog'i, salat bargi, sous",
            is_available=True
        )

        FoodItem.objects.create(
            name="Pepperoni Pizza 32cm",
            category=cat_pizza,
            price=75000,
            preparation_time_mins=20,
            image_url="https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?auto=format&fit=crop&w=600&q=80",
            ingredients="Pishloq Motsarella, achchiq kolbasa Pepperoni, pomidor sousi",
            is_available=True
        )

        FoodItem.objects.create(
            name="Ice Mojito Fresh 0.5L",
            category=cat_drink,
            price=18000,
            preparation_time_mins=5,
            image_url="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80",
            ingredients="Yalpiz, laym, muz, gazlangan ichimlik",
            is_available=True
        )

    return redirect('aslfood_dashboard')


# ==========================================================================
# ASLMARKET RETAIL STORE VIEWS
# ==========================================================================

def dashboard(request):
    """Management Panel Dashboard Overview (/panel/)"""
    total_sales_val = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_debt_val = Debtor.objects.filter(status='active').aggregate(total=Sum('amount'))['total'] or 0
    total_products_count = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=5).count()

    total_cost_val = 0
    for sale in Sale.objects.all():
        for item in sale.items.all():
            if item.product and item.product.cost_price:
                total_cost_val += item.product.cost_price * item.quantity

    net_profit = max(0, total_sales_val - total_cost_val)

    recent_debtors = Debtor.objects.filter(status='active').order_by('-created_at')[:5]
    recent_sales = Sale.objects.order_by('-date')[:5]

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    urgent_debtors_count = Debtor.objects.filter(status='active', created_at__lt=thirty_days_ago).count()

    context = {
        'total_sales': total_sales_val,
        'total_debt': total_debt_val,
        'total_products_count': total_products_count,
        'low_stock_count': low_stock_count,
        'urgent_debtors_count': urgent_debtors_count,
        'net_profit': net_profit,
        'recent_debtors': recent_debtors,
        'recent_sales': recent_sales,
    }
    return render(request, 'panel/dashboard.html', context)


def analytics_view(request):
    """Detailed Store Analytics & Reports (/panel/analytics/)"""
    total_sales_val = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    sales_by_naqd = Sale.objects.filter(payment_method='naqd').aggregate(total=Sum('total_amount'))['total'] or 0
    sales_by_karta = Sale.objects.filter(payment_method='karta').aggregate(total=Sum('total_amount'))['total'] or 0
    sales_by_nasiya = Sale.objects.filter(payment_method='nasiya').aggregate(total=Sum('total_amount'))['total'] or 0

    total_debt_val = Debtor.objects.filter(status='active').aggregate(total=Sum('amount'))['total'] or 0
    total_paid_debt = Debtor.objects.aggregate(total=Sum('initial_amount'))['total'] or 0
    recovered_debt = max(0, total_paid_debt - total_debt_val)

    low_stock_products = Product.objects.filter(stock__lte=5)

    context = {
        'total_sales': total_sales_val,
        'sales_by_naqd': sales_by_naqd,
        'sales_by_karta': sales_by_karta,
        'sales_by_nasiya': sales_by_nasiya,
        'total_debt': total_debt_val,
        'recovered_debt': recovered_debt,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'panel/analytics.html', context)


def debtors_list(request):
    """Debtors Management Section (Qarzdorlar bo'limi - /panel/debtors/)"""
    status_filter = request.GET.get('status', 'all')
    query = request.GET.get('q', '')

    debtors = Debtor.objects.all()

    if status_filter == 'active':
        debtors = debtors.filter(status='active')
    elif status_filter == 'paid':
        debtors = debtors.filter(status='paid')
    elif status_filter == 'overdue':
        thirty_days_ago = timezone.now() - timedelta(days=30)
        debtors = debtors.filter(status='active', created_at__lt=thirty_days_ago)

    if query:
        debtors = debtors.filter(Q(name__icontains=query) | Q(phone__icontains=query))

    total_active_debt = Debtor.objects.filter(status='active').aggregate(total=Sum('amount'))['total'] or 0
    active_count = Debtor.objects.filter(status='active').count()

    context = {
        'debtors': debtors,
        'status_filter': status_filter,
        'query': query,
        'total_active_debt': total_active_debt,
        'active_count': active_count,
    }
    return render(request, 'panel/debtors.html', context)


def debtor_history_api(request, pk):
    """Returns debtor payment history as JSON"""
    debtor = get_object_or_404(Debtor, pk=pk)
    payments = debtor.payments.all()
    history = [
        {
            'id': p.id,
            'date': p.date.strftime('%Y-%m-%d %H:%M'),
            'amount': float(p.amount),
            'note': p.note or "To'lov"
        }
        for p in payments
    ]
    return JsonResponse({
        'name': debtor.name,
        'phone': debtor.phone,
        'current_amount': float(debtor.amount),
        'initial_amount': float(debtor.initial_amount),
        'created_at': debtor.created_at.strftime('%Y-%m-%d %H:%M'),
        'elapsed_time': debtor.elapsed_time_str,
        'payments': history
    })


def debt_receipt_view(request, pk):
    """Printable Debt Payment Receipt View"""
    payment = get_object_or_404(Payment, pk=pk)
    context = {'payment': payment}
    return render(request, 'panel/debt_receipt.html', context)


def add_debtor(request):
    """Add a new debtor manually"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        items = request.POST.get('items_description', '')

        if name and phone and amount:
            amt = float(amount)
            Debtor.objects.create(
                name=name,
                phone=phone,
                amount=amt,
                initial_amount=amt,
                items_description=items,
                status='active',
                created_at=timezone.now()
            )
        return redirect('debtors_list')
    return redirect('debtors_list')


def pay_debt(request):
    """Record partial or full payment for a debtor"""
    if request.method == 'POST':
        debtor_id = request.POST.get('debtor_id')
        pay_amount = float(request.POST.get('amount', 0))
        note = request.POST.get('note', "Naqd to'lov")

        debtor = get_object_or_404(Debtor, pk=debtor_id)

        if pay_amount > 0:
            payment = Payment.objects.create(
                debtor=debtor,
                amount=pay_amount,
                note=note
            )
            debtor.amount = max(0, debtor.amount - pay_amount)
            if debtor.amount == 0:
                debtor.status = 'paid'
            debtor.save()

        return redirect('debtors_list')
    return redirect('debtors_list')


def products_list(request):
    """Product Inventory Management (/panel/products/)"""
    query = request.GET.get('q', '')
    filter_low = request.GET.get('low_stock', '')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    if filter_low:
        products = products.filter(stock__lte=5)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'filter_low': filter_low
    }
    return render(request, 'panel/products.html', context)


def add_product(request):
    """Add a new product to inventory"""
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        cost_price = request.POST.get('cost_price', 0)
        stock = request.POST.get('stock', 0)
        barcode = request.POST.get('barcode', '')
        image_url = request.POST.get('image_url', '')
        description = request.POST.get('description', '')

        category = Category.objects.filter(pk=category_id).first() if category_id else None

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            cost_price=cost_price or 0,
            stock=stock or 0,
            barcode=barcode,
            image_url=image_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
            description=description
        )
        return redirect('products_list')
    return redirect('products_list')


def edit_product(request, pk):
    """Edit existing product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        category_id = request.POST.get('category')
        product.category = Category.objects.filter(pk=category_id).first() if category_id else None
        product.price = request.POST.get('price')
        product.cost_price = request.POST.get('cost_price', 0)
        product.stock = request.POST.get('stock', 0)
        product.barcode = request.POST.get('barcode', '')
        product.image_url = request.POST.get('image_url', product.image_url)
        product.description = request.POST.get('description', '')
        product.save()
        return redirect('products_list')
    return redirect('products_list')


def delete_product(request, pk):
    """Delete product"""
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('products_list')


def pos_view(request):
    """Cashier POS Terminal (/panel/pos/)"""
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'panel/pos.html', context)


@csrf_exempt
def pos_checkout_api(request):
    """AJAX POS Checkout API Endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            payment_method = data.get('payment_method', 'naqd')
            customer_name = data.get('customer_name', 'Xaridor')
            phone = data.get('phone', '')

            if not cart:
                return JsonResponse({'success': False, 'error': 'Savat bo\'sh'})

            total_amount = 0
            sale_items_data = []

            for item in cart:
                prod = Product.objects.get(pk=item['id'])
                qty = int(item['qty'])
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

            debtor = None
            if payment_method == 'nasiya':
                debtor = Debtor.objects.create(
                    name=customer_name or "Nasiya Xaridor",
                    phone=phone or "+998 90 000 00 00",
                    amount=total_amount,
                    initial_amount=total_amount,
                    items_description=f"Kassadan nasiya sotuv: {len(cart)} ta mahsulot",
                    status='active',
                    created_at=timezone.now()
                )

            code = "CHK-" + str(uuid.uuid4())[:8].upper()
            sale = Sale.objects.create(
                sale_code=code,
                total_amount=total_amount,
                payment_method=payment_method,
                customer_name=customer_name or "Xaridor",
                debtor=debtor,
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
                'message': 'Sotuv muvaffaqiyatli saqlandi!'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})


def sales_history(request):
    """Sales History & Profit Reports (/panel/sales/)"""
    sales = Sale.objects.all().order_by('-date')
    total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'sales': sales,
        'total_revenue': total_revenue,
    }
    return render(request, 'panel/sales.html', context)


def export_debtors_csv(request):
    """Export Debtors list as CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="aslmarket_debtors.csv"'

    writer = csv.writer(response)
    writer.writerow(['F.I.Sh', 'Telefon', 'Qarz Summasi', 'Boshlangich Qarz', 'Qarz Olingan Vaqt', 'Otgan Vaqt', 'Holat'])

    for debtor in Debtor.objects.all():
        writer.writerow([
            debtor.name,
            debtor.phone,
            debtor.amount,
            debtor.initial_amount,
            debtor.created_at.strftime('%Y-%m-%d %H:%M'),
            debtor.elapsed_time_str,
            debtor.status
        ])

    return response


def export_sales_csv(request):
    """Export Sales log as CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="aslmarket_sales.csv"'

    writer = csv.writer(response)
    writer.writerow(['Chek Raqami', 'Vaqt', 'Xaridor', 'Tolov Usuli', 'Jami Summa'])

    for sale in Sale.objects.all():
        writer.writerow([
            sale.sale_code,
            sale.date.strftime('%Y-%m-%d %H:%M'),
            sale.customer_name,
            sale.get_payment_method_display(),
            sale.total_amount
        ])

    return response


def seed_demo_data(request):
    """Seeds initial Uzbek demo data into database"""
    cat_elec, _ = Category.objects.get_or_create(name="Elektronika", slug="elektronika")
    cat_app, _ = Category.objects.get_or_create(name="Maishiy Texnika", slug="maishiy-texnika")
    cat_food, _ = Category.objects.get_or_create(name="Oziq-ovqat", slug="oziq-ovqat")
    cat_drink, _ = Category.objects.get_or_create(name="Ichimliklar", slug="ichimliklar")
    cat_home, _ = Category.objects.get_or_create(name="Ro'zg'or buyumlari", slug="rozgor-buyumlari")

    if Product.objects.count() == 0:
        Product.objects.create(
            name='Samsung 43" Smart TV Crystal UHD',
            category=cat_elec,
            price=4500000,
            cost_price=3800000,
            stock=8,
            barcode='8806091234567',
            image_url='https://images.unsplash.com/photo-1593784991095-a205069470b6?auto=format&fit=crop&w=600&q=80',
            description='4K Ultra HD smart televizor, Wi-Fi, HDR10+'
        )
        Product.objects.create(
            name='Artel Muzlatgich HD-345 FW',
            category=cat_app,
            price=3800000,
            cost_price=3200000,
            stock=5,
            barcode='4780001239871',
            image_url='https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?auto=format&fit=crop&w=600&q=80',
            description='NoFrost tizimi, energiya tejamkor A+ sinf'
        )
        Product.objects.create(
            name='Nescafe Gold Qahva 190g',
            category=cat_food,
            price=85000,
            cost_price=68000,
            stock=45,
            barcode='7613032123456',
            image_url='https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80',
            description='Tabiiy eruvchan arabika qahvasi'
        )

    if Debtor.objects.count() == 0:
        now = timezone.now()

        Debtor.objects.create(
            name='Alisher Qodirov',
            phone='+998 90 123 45 67',
            amount=1450000,
            initial_amount=1450000,
            created_at=now - timedelta(days=3, hours=4),
            items_description="Artel Muzlatgich uchun bo'nak, qolgan qarz",
            status='active'
        )

        Debtor.objects.create(
            name='Jahongir Rahimov',
            phone='+998 93 987 65 43',
            amount=520000,
            initial_amount=850000,
            created_at=now - timedelta(days=14, hours=10),
            items_description="Nescafe qahvalari va xaridlar",
            status='active'
        )

        Debtor.objects.create(
            name='Sardorbek Umarov',
            phone='+998 97 555 12 34',
            amount=2800000,
            initial_amount=2800000,
            created_at=now - timedelta(days=42, hours=8),
            items_description="Samsung Smart TV (Nasiya sotuv)",
            status='active'
        )

    return redirect('dashboard')


# ==========================================================================
# ASLFOOD MOBILE APP REST API ENDPOINTS
# /api/food/... — React Native Android ilovasi uchun
# ==========================================================================

def api_food_menu(request):
    """
    GET /api/food/menu/
    Barcha mavjud taomlarni kategoriyalar bilan qaytaradi.
    """
    categories = FoodCategory.objects.prefetch_related('items').all()
    result = []
    for cat in categories:
        items = []
        for item in cat.items.filter(is_available=True):
            items.append({
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'preparation_time_mins': item.preparation_time_mins,
                'is_available': item.is_available,
                'image_url': item.image_url or '',
                'ingredients': item.ingredients or '',
            })
        result.append({
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'items': items,
        })
    return JsonResponse({'success': True, 'categories': result})


def api_food_menu_all(request):
    """
    GET /api/food/menu/all/
    Barcha taomlar (admin panel uchun - mavjud bo'lmagan ham)
    """
    items = FoodItem.objects.select_related('category').all()
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'name': item.name,
            'category': item.category.name if item.category else '',
            'category_id': item.category.id if item.category else None,
            'price': float(item.price),
            'preparation_time_mins': item.preparation_time_mins,
            'is_available': item.is_available,
            'image_url': item.image_url or '',
            'ingredients': item.ingredients or '',
        })
    return JsonResponse({'success': True, 'items': data})


@csrf_exempt
def api_food_toggle(request, pk):
    """
    POST /api/food/menu/toggle/<pk>/
    Taomni mavjud/tugagan holatga o'tkazish
    """
    item = get_object_or_404(FoodItem, pk=pk)
    item.is_available = not item.is_available
    item.save()
    return JsonResponse({
        'success': True,
        'id': item.id,
        'is_available': item.is_available,
        'message': f"{'Mavjud' if item.is_available else 'Tugagan'} holatga o'tkazildi"
    })


@csrf_exempt
def api_food_add_item(request):
    """
    POST /api/food/menu/add/
    Yangi taom qo'shish (JSON body)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Faqat POST'})
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        category_id = data.get('category_id')
        price = data.get('price')
        prep_time = data.get('preparation_time_mins', 15)
        image_url = data.get('image_url', '')
        ingredients = data.get('ingredients', '')

        if not name or not price:
            return JsonResponse({'success': False, 'error': 'Nom va narx kiritilishi shart'})

        category = FoodCategory.objects.filter(pk=category_id).first() if category_id else None
        if not category:
            return JsonResponse({'success': False, 'error': 'Kategoriya topilmadi'})

        item = FoodItem.objects.create(
            name=name,
            category=category,
            price=price,
            preparation_time_mins=prep_time or 15,
            image_url=image_url or 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80',
            ingredients=ingredients,
            is_available=True,
        )
        return JsonResponse({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'category': item.category.name,
                'is_available': item.is_available,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def api_food_edit_item(request, pk):
    """
    POST /api/food/menu/edit/<pk>/
    Mavjud taomni tahrirlash
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Faqat POST'})
    try:
        item = get_object_or_404(FoodItem, pk=pk)
        data = json.loads(request.body)

        if 'name' in data:
            item.name = data['name'].strip()
        if 'price' in data:
            item.price = data['price']
        if 'preparation_time_mins' in data:
            item.preparation_time_mins = data['preparation_time_mins']
        if 'image_url' in data:
            item.image_url = data['image_url']
        if 'ingredients' in data:
            item.ingredients = data['ingredients']
        if 'category_id' in data:
            cat = FoodCategory.objects.filter(pk=data['category_id']).first()
            if cat:
                item.category = cat
        item.save()

        return JsonResponse({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'category': item.category.name,
                'is_available': item.is_available,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def api_food_delete_item(request, pk):
    """
    POST /api/food/menu/delete/<pk>/
    Taomni o'chirish
    """
    item = get_object_or_404(FoodItem, pk=pk)
    item.delete()
    return JsonResponse({'success': True, 'message': 'Taom o\'chirildi'})


def api_food_categories(request):
    """
    GET /api/food/categories/
    Barcha kategoriyalarni qaytaradi
    """
    cats = FoodCategory.objects.all()
    data = [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in cats]
    return JsonResponse({'success': True, 'categories': data})


def api_food_orders(request):
    """
    GET /api/food/orders/
    Barcha buyurtmalarni status bo'yicha qaytaradi (kitchen board uchun)
    Query params: ?status=new|preparing|delivering|completed
    """
    status_filter = request.GET.get('status', '')

    qs = FoodOrder.objects.prefetch_related('items').all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    else:
        # Kitchen board: faqat faol buyurtmalar
        qs = qs.exclude(status='cancelled').order_by('created_at')

    def serialize_order(order):
        items = []
        for it in order.items.all():
            items.append({
                'id': it.id,
                'food_name': it.food_name,
                'quantity': it.quantity,
                'unit_price': float(it.unit_price),
                'total_price': float(it.total_price),
            })
        return {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'phone': order.phone,
            'delivery_address': order.delivery_address or '',
            'total_amount': float(order.total_amount),
            'payment_method': order.payment_method,
            'order_type': order.order_type,
            'order_type_display': order.get_order_type_display(),
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items,
        }

    data = [serialize_order(o) for o in qs]
    return JsonResponse({'success': True, 'orders': data, 'count': len(data)})


def api_food_order_detail(request, pk):
    """
    GET /api/food/orders/<pk>/
    Bitta buyurtma tafsilotlari
    """
    order = get_object_or_404(FoodOrder, pk=pk)
    items = []
    for it in order.items.all():
        items.append({
            'id': it.id,
            'food_name': it.food_name,
            'quantity': it.quantity,
            'unit_price': float(it.unit_price),
            'total_price': float(it.total_price),
        })
    return JsonResponse({
        'success': True,
        'order': {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'phone': order.phone,
            'delivery_address': order.delivery_address or '',
            'total_amount': float(order.total_amount),
            'payment_method': order.payment_method,
            'order_type': order.order_type,
            'order_type_display': order.get_order_type_display(),
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items,
        }
    })


@csrf_exempt
def api_food_order_status_update(request):
    """
    POST /api/food/orders/status/
    Body: { "order_id": 1, "new_status": "preparing" }
    Buyurtma holatini yangilash
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Faqat POST'})
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('new_status')

        valid_statuses = ['new', 'preparing', 'delivering', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': f'Noto\'g\'ri status. Qabul qilinadiganlar: {valid_statuses}'})

        order = get_object_or_404(FoodOrder, pk=order_id)
        order.status = new_status
        order.save()

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'order_code': order.order_code,
            'new_status': new_status,
            'status_display': order.get_status_display(),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def api_food_place_order(request):
    """
    POST /api/food/orders/place/
    Mijoz tomonidan yangi buyurtma berish (aslfood_order_api bilan bir xil mantiq,
    lekin faqat JSON in/out)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Faqat POST'})
    try:
        data = json.loads(request.body)
        cart = data.get('cart', [])
        customer_name = data.get('customer_name', 'Mijoz').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '')
        order_type = data.get('order_type', 'delivery')

        if not cart:
            return JsonResponse({'success': False, 'error': 'Savat bo\'sh'})
        if not customer_name or not phone:
            return JsonResponse({'success': False, 'error': 'Ism va telefon kiritilishi shart'})

        total_amount = 0
        order_items = []

        for item in cart:
            food = FoodItem.objects.get(pk=item['id'])
            if not food.is_available:
                return JsonResponse({'success': False, 'error': f"{food.name} hozir mavjud emas"})
            qty = int(item['qty'])
            subtotal = food.price * qty
            total_amount += subtotal
            order_items.append({
                'food': food,
                'name': food.name,
                'qty': qty,
                'price': food.price,
            })

        code = "FOOD-" + str(uuid.uuid4())[:6].upper()
        order = FoodOrder.objects.create(
            order_code=code,
            customer_name=customer_name,
            phone=phone,
            delivery_address=address,
            total_amount=total_amount,
            order_type=order_type,
            status='new',
            created_at=timezone.now(),
        )

        for it in order_items:
            FoodOrderItem.objects.create(
                order=order,
                food_item=it['food'],
                food_name=it['name'],
                quantity=it['qty'],
                unit_price=it['price'],
            )

        return JsonResponse({
            'success': True,
            'order_code': code,
            'order_id': order.id,
            'total_amount': float(total_amount),
            'message': 'Buyurtmangiz qabul qilindi! Oshpaz tayyorlamoqda 🍳',
        })
    except FoodItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Taom topilmadi'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def api_food_stats(request):
    """
    GET /api/food/stats/
    Kitchen dashboard statistikasi: bugungi tushum, buyurtmalar soni, holat bo'yicha
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Bugungi statistika
    today_orders = FoodOrder.objects.filter(created_at__gte=today_start)
    today_completed = today_orders.filter(status='completed')
    today_revenue = today_completed.aggregate(total=Sum('total_amount'))['total'] or 0

    # Haftalik statistika
    week_orders = FoodOrder.objects.filter(created_at__gte=week_start)
    week_completed = week_orders.filter(status='completed')
    week_revenue = week_completed.aggregate(total=Sum('total_amount'))['total'] or 0

    # Hozirgi faol buyurtmalar soni
    active_new = FoodOrder.objects.filter(status='new').count()
    active_preparing = FoodOrder.objects.filter(status='preparing').count()
    active_delivering = FoodOrder.objects.filter(status='delivering').count()

    # Jami statistika
    total_revenue = FoodOrder.objects.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = FoodOrder.objects.filter(status='completed').count()

    # Eng ko'p sotilgan taomlar (top 5)
    top_items = (
        FoodOrderItem.objects
        .values('food_name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )

    return JsonResponse({
        'success': True,
        'stats': {
            'today': {
                'revenue': float(today_revenue),
                'orders_count': today_orders.count(),
                'completed_count': today_completed.count(),
            },
            'week': {
                'revenue': float(week_revenue),
                'orders_count': week_orders.count(),
                'completed_count': week_completed.count(),
            },
            'total': {
                'revenue': float(total_revenue),
                'completed_orders': total_orders,
            },
            'active_now': {
                'new': active_new,
                'preparing': active_preparing,
                'delivering': active_delivering,
            },
            'top_items': list(top_items),
        }
    })


def api_food_order_by_code(request, code):
    """
    GET /api/food/orders/track/<code>/
    Buyurtma kodi orqali holat kuzatish (mijoz tomonidan)
    """
    order = get_object_or_404(FoodOrder, order_code=code.upper())
    items = []
    for it in order.items.all():
        items.append({
            'food_name': it.food_name,
            'quantity': it.quantity,
            'unit_price': float(it.unit_price),
            'total_price': float(it.total_price),
        })

    status_steps = {
        'new': 1,
        'preparing': 2,
        'delivering': 3,
        'completed': 4,
        'cancelled': 0,
    }

    return JsonResponse({
        'success': True,
        'order': {
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'status': order.status,
            'status_display': order.get_status_display(),
            'status_step': status_steps.get(order.status, 1),
            'order_type': order.order_type,
            'order_type_display': order.get_order_type_display(),
            'total_amount': float(order.total_amount),
            'delivery_address': order.delivery_address or '',
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'items': items,
        }
    })
