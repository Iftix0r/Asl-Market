from django.urls import path
from . import views

urlpatterns = [
    # AslFood Public Storefront (asosiy sahifa)
    path('', views.storefront, name='storefront'),

    # AslFood Public Order API
    path('aslfood/order/', views.aslfood_order_api, name='aslfood_order_api'),

    # AslFood Kitchen & Fast Food Panel routes (/aslfood/panel/...)
    path('aslfood/panel/', views.aslfood_dashboard, name='aslfood_dashboard'),
    path('aslfood/panel/status-update/', views.aslfood_update_status_api, name='aslfood_update_status_api'),
    path('aslfood/panel/menu/', views.aslfood_menu_list, name='aslfood_menu_list'),
    path('aslfood/panel/menu/add/', views.aslfood_add_item, name='aslfood_add_item'),
    path('aslfood/panel/menu/toggle/<int:pk>/', views.aslfood_toggle_availability_api, name='aslfood_toggle_availability_api'),
    path('aslfood/panel/receipt/<int:pk>/', views.aslfood_receipt_view, name='aslfood_receipt_view'),
    path('aslfood/panel/seed/', views.aslfood_seed_data, name='aslfood_seed_data'),

    # ==========================================================================
    # ASLFOOD MOBILE APP REST API ENDPOINTS (/api/food/...)
    # ==========================================================================

    # Menu
    path('api/food/menu/', views.api_food_menu, name='api_food_menu'),
    path('api/food/menu/all/', views.api_food_menu_all, name='api_food_menu_all'),
    path('api/food/menu/add/', views.api_food_add_item, name='api_food_add_item_api'),
    path('api/food/menu/edit/<int:pk>/', views.api_food_edit_item, name='api_food_edit_item'),
    path('api/food/menu/delete/<int:pk>/', views.api_food_delete_item, name='api_food_delete_item'),
    path('api/food/menu/toggle/<int:pk>/', views.api_food_toggle, name='api_food_toggle'),
    path('api/food/categories/', views.api_food_categories, name='api_food_categories'),

    # Orders
    path('api/food/orders/', views.api_food_orders, name='api_food_orders'),
    path('api/food/orders/user/<str:telegram_id>/', views.api_food_orders_user, name='api_food_orders_user'),
    path('api/food/orders/place/', views.api_food_place_order, name='api_food_place_order'),
    path('api/food/orders/status/', views.api_food_order_status_update, name='api_food_order_status_update'),
    path('api/food/orders/<int:pk>/', views.api_food_order_detail, name='api_food_order_detail'),
    path('api/food/orders/track/<str:code>/', views.api_food_order_by_code, name='api_food_order_by_code'),

    # Stats / Analytics
    path('api/food/stats/', views.api_food_stats, name='api_food_stats'),

    # Telegram Bot Webhook
    path('api/telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('api/telegram/set-webhook/', views.set_telegram_webhook, name='set_telegram_webhook'),
]

