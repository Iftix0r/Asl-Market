from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
import json
import uuid

from .models import BotUser, FoodCategory, FoodItem, FoodOrder, FoodOrderItem
from .telegram_notify import send_order_to_group, send_status_update_to_group


# ==========================================================================
# ASLFOOD TELEGRAM MINI APP — PUBLIC STOREFRONT
# ==========================================================================

def storefront(request):
    """Telegram Mini App — public customer-facing AslFood menu."""
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    cat_slug = request.GET.get('category', '').strip()

    food_items = FoodItem.objects.select_related('category').filter(is_available=True)
    food_categories = FoodCategory.objects.all()

    if cat_slug:
        food_items = food_items.filter(category__slug=cat_slug)
    if query:
        food_items = food_items.filter(Q(name__icontains=query) | Q(ingredients__icontains=query))

    webapp_base_url = getattr(settings, 'WEBAPP_BASE_URL', '')

    context = {
        'food_items': food_items,
        'food_categories': food_categories,
        'selected_category': cat_slug,
        'query': query,
        'webapp_base_url': webapp_base_url,
    }
    return render(request, 'storefront.html', context)


# ==========================================================================
# ASLFOOD KITCHEN & FAST FOOD PANEL VIEWS
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


def aslfood_customers(request):
    """Customer directory with Telegram profile data and order history."""
    # Auto-link unlinked orders to BotUsers if telegram_id exists
    unlinked_orders = FoodOrder.objects.filter(bot_user__isnull=True).exclude(telegram_id__isnull=True).exclude(telegram_id='')
    for o_unlinked in unlinked_orders:
        buser, _ = BotUser.objects.get_or_create(
            telegram_id=str(o_unlinked.telegram_id),
            defaults={
                'first_name': o_unlinked.customer_name,
                'phone': o_unlinked.phone,
                'joined_at': o_unlinked.created_at,
                'last_seen': o_unlinked.created_at,
            }
        )
        o_unlinked.bot_user = buser
        o_unlinked.save(update_fields=['bot_user'])

    customers = BotUser.objects.prefetch_related('orders').all()
    total_customers = customers.count()
    total_orders_count = sum(len(c.orders.all()) for c in customers)

    context = {
        'customers': customers,
        'total_customers': total_customers,
        'total_orders_count': total_orders_count,
    }
    return render(request, 'aslfood/customers.html', context)


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
            comment = data.get('comment', '').strip()
            telegram_id = data.get('telegram_id', '').strip()
            items = data.get('items', [])

            if not items:
                return JsonResponse({'success': False, 'error': "Savatcha bo'sh"})

            with transaction.atomic():
                total_amount = 0
                order_code = "FD-" + str(uuid.uuid4())[:8].upper()

                bot_user = None
                if telegram_id:
                    bot_user, _ = BotUser.objects.get_or_create(
                        telegram_id=str(telegram_id),
                        defaults={
                            'first_name': customer_name,
                            'phone': phone,
                            'joined_at': timezone.now(),
                            'last_seen': timezone.now(),
                        }
                    )
                    if phone and not bot_user.phone:
                        bot_user.phone = phone
                        bot_user.save(update_fields=['phone'])

                order = FoodOrder.objects.create(
                    order_code=order_code,
                    customer_name=customer_name,
                    phone=phone,
                    delivery_address=delivery_address,
                    order_type=order_type,
                    payment_method=payment_method,
                    comment=comment,
                    telegram_id=telegram_id,
                    bot_user=bot_user,
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

            # Telegram guruhga va mijozga bildirishnoma yuborish (transaction tashqarisida)
            try:
                send_order_to_group(order)
                send_status_update_to_customer(order)
            except Exception:
                pass  # Telegram xatosi buyurtmani bloklamasin

            return JsonResponse({
                'success': True,
                'order_code': order_code,
                'total_amount': float(total_amount),
                'message': 'Buyurtmangiz oshxonaga topshirildi!'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"})


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

            # Holat o'zgarganda guruhga hamda mijozga Telegram xabar yuboriladi
            if new_status in ('completed', 'cancelled', 'delivering'):
                try:
                    send_status_update_to_group(order)
                    send_status_update_to_customer(order)
                except Exception:
                    pass

            return JsonResponse({'success': True, 'new_status': new_status, 'order_code': order.order_code})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"})


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
# DEMO DATA SEEDER
# ==========================================================================

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

        # Mock Bot Users
        if BotUser.objects.count() == 0:
            u1 = BotUser.objects.create(
                telegram_id="589210492",
                first_name="Dilshod",
                last_name="Rahimov",
                username="dilshod_rahimov",
                phone="+998974443322",
                language_code="uz"
            )
            u2 = BotUser.objects.create(
                telegram_id="194820184",
                first_name="Alisher",
                last_name="Karimov",
                username="alisher_k",
                phone="+998901110099",
                language_code="uz"
            )
        else:
            u1 = BotUser.objects.first()
            u2 = BotUser.objects.last()

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
                status="new",
                bot_user=u1,
                telegram_id=u1.telegram_id if u1 else None
            )
            if item_lavash and item_pizza:
                FoodOrderItem.objects.create(order=o1, food_item=item_lavash, food_name=item_lavash.name, quantity=1, unit_price=item_lavash.price)
                FoodOrderItem.objects.create(order=o1, food_item=item_pizza, food_name=item_pizza.name, quantity=1, unit_price=item_pizza.price)

            FoodOrder.objects.create(
                order_code="FD-4401B",
                customer_name="Alisher aka (Stol #4)",
                phone="+998901110099",
                delivery_address="Stol #4",
                total_amount=42000,
                order_type="table",
                status="preparing",
                bot_user=u2,
                telegram_id=u2.telegram_id if u2 else None
            )

    return HttpResponse("AslFood Fast-Food Demo Ma'lumotlari kiritildi! <a href='/panel/'>Oshxona Paneliga o'tish</a>")


# ==========================================================================
# ASLFOOD MOBILE APP REST API ENDPOINTS
# ==========================================================================

def api_food_menu(request):
    """GET /api/food/menu/ — Get list of available food menu items"""
    from django.db.models import Q
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

def api_food_orders_user(request, telegram_id):
    """GET /api/food/orders/user/<telegram_id>/ — Fetch user's past orders"""
    orders = FoodOrder.objects.filter(telegram_id=telegram_id).order_by('-created_at')[:20]
    data = []
    for order in orders:
        items = order.items.all()
        item_data = [{'name': i.food_name, 'qty': i.quantity, 'price': float(i.unit_price)} for i in items]
        data.append({
            'id': order.id,
            'order_code': order.order_code,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'items': item_data
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
            'comment': order.comment,
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
# TELEGRAM NOTIFICATION HELPER
# ==========================================================================

def send_telegram_notification(text):
    """Optional Helper to dispatch instant Telegram alert on new orders"""
    import urllib.request
    import urllib.parse
    from django.conf import settings
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


# ==========================================================================
# TELEGRAM BOT WEBHOOK VIEWS
def _upsert_bot_user_from_telegram_dict(data):
    """
    Extracts user details from Telegram update payload and saves/updates BotUser in DB.
    Guarantees that ANY interaction with the bot persists the customer to Django DB.
    """
    try:
        from_user = None
        if isinstance(data, dict):
            if 'message' in data and isinstance(data['message'], dict):
                from_user = data['message'].get('from')
            elif 'edited_message' in data and isinstance(data['edited_message'], dict):
                from_user = data['edited_message'].get('from')
            elif 'callback_query' in data and isinstance(data['callback_query'], dict):
                from_user = data['callback_query'].get('from')
            elif 'inline_query' in data and isinstance(data['inline_query'], dict):
                from_user = data['inline_query'].get('from')
            elif 'my_chat_member' in data and isinstance(data['my_chat_member'], dict):
                from_user = data['my_chat_member'].get('from')

        if not from_user or not isinstance(from_user, dict):
            return None

        tg_id = str(from_user.get('id', '')).strip()
        if not tg_id:
            return None

        first_name = from_user.get('first_name', '') or ''
        last_name = from_user.get('last_name', '') or ''
        username = from_user.get('username')
        language_code = from_user.get('language_code')

        obj, created = BotUser.objects.get_or_create(
            telegram_id=tg_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'language_code': language_code,
                'joined_at': timezone.now(),
                'last_seen': timezone.now(),
            }
        )
        if not created:
            updated_fields = ['last_seen']
            obj.last_seen = timezone.now()
            if first_name and obj.first_name != first_name:
                obj.first_name = first_name
                updated_fields.append('first_name')
            if last_name and obj.last_name != last_name:
                obj.last_name = last_name
                updated_fields.append('last_name')
            if username and obj.username != username:
                obj.username = username
                updated_fields.append('username')
            if language_code and obj.language_code != language_code:
                obj.language_code = language_code
                updated_fields.append('language_code')
            obj.save(update_fields=updated_fields)
        return obj
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in _upsert_bot_user_from_telegram_dict: {e}")
        return None


def _handle_telegram_update_builtin(data):
    """
    Built-in pure Python Telegram update handler.
    Does NOT depend on python-telegram-bot package, guaranteeing 100% reliability on cPanel.
    """
    import urllib.request
    import urllib.parse

    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    webapp_url = getattr(settings, 'WEBAPP_BASE_URL', '').rstrip('/') + '/'

    if not bot_token:
        return

    def api_call(method, payload):
        try:
            url = f"https://api.telegram.org/bot{bot_token}/{method}"
            body = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass

    # 1. Message Updates
    if 'message' in data:
        msg = data['message']
        chat_id = msg.get('chat', {}).get('id')
        text = msg.get('text', '').strip()
        first_name = msg.get('from', {}).get('first_name', 'Mehmon')

        if not chat_id:
            return

        if text.startswith('/start'):
            reply_markup = {
                'inline_keyboard': [
                    [{'text': '🍔 Menyu va Buyurtma Berish', 'web_app': {'url': webapp_url}}],
                    [
                        {'text': "📞 Bog'lanish", 'url': 'https://t.me/aslfoodsupport'},
                        {'text': 'ℹ️ Haqimizda', 'callback_data': 'about'}
                    ]
                ]
            }
            message_text = (
                f"Assalomu alaykum, <b>{first_name}</b>! 👋\n\n"
                f"🍔 <b>AslFood</b> botiga xush kelibsiz!\n\n"
                f"Bizning menyumizdan mazali taomlarni tanlang va "
                f"<b>15–25 daqiqada</b> dostavka qilib beramiz 🛵\n\n"
                f"👇 <b>«Menyu va Buyurtma Berish»</b> tugmasini bosing:"
            )
            api_call('sendMessage', {
                'chat_id': chat_id,
                'text': message_text,
                'parse_mode': 'HTML',
                'reply_markup': reply_markup
            })

        elif text.startswith('/menu'):
            reply_markup = {
                'inline_keyboard': [
                    [{'text': '🍔 Menyuni ochish', 'web_app': {'url': webapp_url}}]
                ]
            }
            api_call('sendMessage', {
                'chat_id': chat_id,
                'text': "🍽️ <b>AslFood Menyu</b>\n\nQuyidagi tugmani bosing:",
                'parse_mode': 'HTML',
                'reply_markup': reply_markup
            })

        elif text.startswith('/orders'):
            from store.models import FoodOrder
            active = list(
                FoodOrder.objects.filter(status__in=["new", "preparing", "delivering"]).order_by("created_at")[:10]
            )
            if not active:
                api_call('sendMessage', {'chat_id': chat_id, 'text': "✅ Hozircha faol buyurtmalar yo'q."})
            else:
                STATUS_EMOJI = {"new": "🟡 Yangi", "preparing": "🍳 Tayyorlanmoqda", "delivering": "🛵 Yo'lda"}
                out = "📋 <b>Faol buyurtmalar:</b>\n\n"
                for o in active:
                    out += f"#{o.order_code} — {o.customer_name} ({o.phone})\n   📊 {STATUS_EMOJI.get(o.status, o.status)} | 💰 {int(o.total_amount):,} so'm\n\n"
                api_call('sendMessage', {'chat_id': chat_id, 'text': out, 'parse_mode': 'HTML'})

        else:
            reply_markup = {
                'inline_keyboard': [
                    [{'text': '🍔 Menyuni ochish', 'web_app': {'url': webapp_url}}]
                ]
            }
            api_call('sendMessage', {
                'chat_id': chat_id,
                'text': "Menyu uchun /start yoki /menu buyrug'ini yuboring 👇",
                'reply_markup': reply_markup
            })

    # 2. Callback Query Updates
    elif 'callback_query' in data:
        cb = data['callback_query']
        cb_id = cb.get('id')
        chat_id = cb.get('message', {}).get('chat', {}).get('id')
        cb_data = cb.get('data')

        if cb_id:
            api_call('answerCallbackQuery', {'callback_query_id': cb_id})

        if cb_data == 'about' and chat_id:
            about_text = (
                "🍔 <b>AslFood</b>\n\n"
                "Biz tez va mazali taomlar yetkazib beramiz.\n"
                "Lavash, Pizza, Gamburger va ko'p boshqa taomlar!\n\n"
                "📍 Manzil: ...\n"
                "📞 Tel: ...\n"
                "🕒 Ish vaqti: 09:00 — 23:00"
            )
            api_call('sendMessage', {'chat_id': chat_id, 'text': about_text, 'parse_mode': 'HTML'})


@csrf_exempt
def telegram_webhook(request):
    """
    Telegram Webhook Endpoint (/api/telegram/webhook/)
    Telegram serverlaridan keluvchi POST so'rovlarini qabul qiladi.
    cPanel / Passenger WSGI hamda ASGI serverlar uchun 100% xavfsiz.
    """
    if request.method != 'POST':
        return HttpResponse("AslFood Telegram Webhook Endpoint Active", status=200)

    try:
        data = json.loads(request.body.decode('utf-8'))
        _upsert_bot_user_from_telegram_dict(data)
    except Exception:
        return HttpResponse("Invalid JSON", status=400)

    # Try python-telegram-bot first, fallback to pure Python handler if missing/fails
    try:
        from bot import create_bot_app
        from telegram import Update
        import asyncio

        async def process_update_async():
            app = create_bot_app()
            if not app:
                return False
            async with app:
                await app.start()
                update = Update.de_json(data, app.bot)
                await app.process_update(update)
                await app.stop()
            return True

        asyncio.run(process_update_async())
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"python-telegram-bot failed, using built-in handler: {e}")
        _handle_telegram_update_builtin(data)

    return HttpResponse("OK", status=200)




def set_telegram_webhook(request):
    """
    Telegram Webhook'ni sozlash uchun yordamchi view (/api/telegram/set-webhook/)
    GET parametrlar: ?action=set (default), ?action=delete, ?action=info
    """
    import urllib.request
    import urllib.parse

    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    webapp_base_url = getattr(settings, 'WEBAPP_BASE_URL', '').rstrip('/')

    if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
        return JsonResponse({'status': 'error', 'message': 'settings.py da TELEGRAM_BOT_TOKEN to\'ldirilmagan'}, status=400)

    webhook_url = f"{webapp_base_url}/api/telegram/webhook/"
    action = request.GET.get('action', 'set')

    if action == 'delete':
        api_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    elif action == 'info':
        api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    else:
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={urllib.parse.quote(webhook_url)}"

    try:
        req = urllib.request.Request(api_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            result['target_webhook_url'] = webhook_url
            return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

