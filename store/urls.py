from django.urls import path
from . import views

urlpatterns = [
    # Client
    path('landing/', views.landing_3d, name='landing_3d'),
    path('', views.index, name='index'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('placeOrder/', views.place_order, name='place_order'),
    path('orders/', views.order_list, name='order_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile_view'),

    # Admin Dashboard (using /admin_dashboard to avoid conflict with built-in django admin)
    path('admin_dashboard/', views.admin_index, name='admin_index'),
    path('admin_dashboard/market-basket/', views.admin_market_basket, name='admin_mba'),
    
    # Admin Products
    path('admin_dashboard/products/', views.admin_list_products, name='admin_products'),
    path('admin_dashboard/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin_dashboard/products/save/', views.admin_save_product, name='admin_save_product'),
    path('admin_dashboard/products/delete/<int:id>/', views.admin_delete_product, name='admin_delete_product'),
    path('admin_dashboard/products/edit/<int:id>/', views.admin_edit_product, name='admin_edit_product'),

    # Admin Categories
    path('admin_dashboard/categories/', views.admin_list_categories, name='admin_categories'),
    path('admin_dashboard/categories/save/', views.admin_save_category, name='admin_save_category'),
    path('admin_dashboard/categories/delete/<int:id>/', views.admin_delete_category, name='admin_delete_category'),

    # Admin Orders
    path('admin_dashboard/orders/', views.admin_list_orders, name='admin_orders'),
    path('admin_dashboard/orders/detail/<int:id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin_dashboard/orders/update-status/', views.admin_update_order_status, name='admin_update_order_status'),

    # Admin Users
    path('admin_dashboard/users/', views.admin_list_users, name='admin_users'),
    path('admin_dashboard/users/create-employee/', views.admin_create_employee, name='admin_create_employee'),
    path('admin_dashboard/users/update-role/', views.admin_update_user_role, name='admin_update_user_role'),
    path('admin_dashboard/users/toggle-status/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin_dashboard/users/delete/<int:id>/', views.admin_delete_user, name='admin_delete_user'),

    # Admin Inventory
    path('admin_dashboard/inventory/', views.admin_inventory, name='admin_inventory'),
    path('admin_dashboard/inventory/add-stock/', views.admin_add_stock, name='admin_add_stock'),

    # Admin Price Requests
    path('admin_dashboard/price-requests/', views.admin_price_requests, name='admin_price_requests'),
    path('admin_dashboard/price-requests/<int:id>/<str:action>/', views.admin_handle_price_request, name='admin_handle_price_request'),

    # Employee Views
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee_dashboard/inventory/', views.employee_inventory, name='employee_inventory'),
    path('employee_dashboard/create-order/', views.employee_create_order, name='employee_create_order'),
    path('employee_dashboard/request-price/', views.employee_request_price, name='employee_request_price'),
    path('employee_dashboard/orders/', views.employee_manage_orders, name='employee_manage_orders'),
    path('employee_dashboard/orders/update/', views.employee_update_order, name='employee_update_order'),

    path('kho/phieu-kho/', views.danh_sach_phieu_kho, name='danh_sach_phieu_kho'),
    path('kho/phieu-kho/tao/', views.tao_phieu_kho, name='tao_phieu_kho'),
    path('kho/phieu-kho/<int:ma_id>/', views.chi_tiet_phieu_kho, name='chi_tiet_phieu_kho'),
    path('kho/chi-nhanh/', views.quan_ly_chi_nhanh, name='quan_ly_chi_nhanh'),
    path('kho/chi-nhanh/them/', views.them_chi_nhanh, name='them_chi_nhanh'),
    path('kho/chi-nhanh/xoa/<int:ma_id>/', views.xoa_chi_nhanh, name='xoa_chi_nhanh'),
    path('kho/nha-cung-cap/', views.quan_ly_nha_cung_cap, name='quan_ly_nha_cung_cap'),
    path('kho/nha-cung-cap/them/', views.them_nha_cung_cap, name='them_nha_cung_cap'),
    path('kho/nha-cung-cap/xoa/<int:ma_id>/', views.xoa_nha_cung_cap, name='xoa_nha_cung_cap'),
]
