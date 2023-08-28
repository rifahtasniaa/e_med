# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('signup_success/', views.signup_success, name='signup_success'),
    path('product_list/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('category_list/', views.category_list, name='category_list'),
    path('cart/', views.cart_view, name='cart'),
    path('ocr_scan/', views.ocr_scan, name='ocr_scan'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('add_from_ocr/', views.add_from_ocr, name='add_from_ocr'),
    path('cart_list/', views.cart_list, name='cart_list'),
    path('logout/', views.user_logout, name='logout'),
    path('update_cart/<int:pk>/', views.update_cart, name='update_cart'),
    path('add_selected_to_cart/', views.add_selected_to_cart, name='add_selected_to_cart'),
    path('add_all_to_cart/', views.add_all_to_cart, name='add_all_to_cart'),
    path('buy_products/', views.buy_products, name='buy_products'),
    path('delivery_info/', views.delivery_info, name='delivery_info'),
    path('edit_delivery_info/<int:pk>/', views.edit_delivery_info, name='edit_delivery_info'),
    path('select_from_history/', views.select_from_history, name='select_from_history'),
    path('payment/', views.payment_view, name='payment'),  
    path('delivery_history/', views.delivery_history, name='delivery_history'),
    # ... other URL patterns ...
    path('remove_delivery_info/<int:delivery_info_id>/', views.remove_delivery_info, name='remove_delivery_info'),
    path('send_cash_on_delivery_email/', views.send_cash_on_delivery_email, name='send_cash_on_delivery_email'),
    path('payment_confirmation/', views.payment_confirmation, name='payment_confirmation'),

]
