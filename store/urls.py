from django.urls import path
from . import views

urlpatterns = [
    # Storefront
    path('', views.storefront, name='storefront'),
    path('storefront/checkout/', views.online_checkout_api, name='online_checkout_api'),

    # AslFood Storefront Order API
    path('aslfood/order/', views.aslfood_order_api, name='aslfood_order_api'),

    # AslFood Kitchen & Fast Food Panel routes (/aslfood/panel/...)
    path('aslfood/panel/', views.aslfood_dashboard, name='aslfood_dashboard'),
    path('aslfood/panel/status-update/', views.aslfood_update_status_api, name='aslfood_update_status_api'),
    path('aslfood/panel/menu/', views.aslfood_menu_list, name='aslfood_menu_list'),
    path('aslfood/panel/menu/add/', views.aslfood_add_item, name='aslfood_add_item'),
    path('aslfood/panel/menu/toggle/<int:pk>/', views.aslfood_toggle_availability_api, name='aslfood_toggle_availability_api'),
    path('aslfood/panel/receipt/<int:pk>/', views.aslfood_receipt_view, name='aslfood_receipt_view'),
    path('aslfood/panel/seed/', views.aslfood_seed_data, name='aslfood_seed_data'),

    # AslMarket Retail Admin Panel routes (/panel/...)
    path('panel/', views.dashboard, name='dashboard'),
    path('panel/analytics/', views.analytics_view, name='analytics_view'),

    # Debtors routes (Qarzdorlar bo'limi)
    path('panel/debtors/', views.debtors_list, name='debtors_list'),
    path('panel/debtors/add/', views.add_debtor, name='add_debtor'),
    path('panel/debtors/pay/', views.pay_debt, name='pay_debt'),
    path('panel/debtors/history/<int:pk>/', views.debtor_history_api, name='debtor_history_api'),
    path('panel/debtors/receipt/<int:pk>/', views.debt_receipt_view, name='debt_receipt_view'),
    path('panel/debtors/export/', views.export_debtors_csv, name='export_debtors_csv'),

    # Products routes
    path('panel/products/', views.products_list, name='products_list'),
    path('panel/products/add/', views.add_product, name='add_product'),
    path('panel/products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('panel/products/delete/<int:pk>/', views.delete_product, name='delete_product'),

    # POS Kassa routes
    path('panel/pos/', views.pos_view, name='pos_view'),
    path('panel/pos/checkout/', views.pos_checkout_api, name='pos_checkout_api'),

    # Sales & Reports
    path('panel/sales/', views.sales_history, name='sales_history'),
    path('panel/sales/export/', views.export_sales_csv, name='export_sales_csv'),

    # Seed Demo Data
    path('panel/seed/', views.seed_demo_data, name='seed_demo_data'),
]
