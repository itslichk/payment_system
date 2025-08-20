from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('api/users/', views.users_api, name='users_api'),
    path('api/users/<int:user_id>/', views.user_api, name='user_api'),
    path('api/products/', views.products_api, name='products_api'),
    path('api/products/<int:product_id>/', views.product_api, name='product_api'),
    path('api/payments/', views.payments_api, name='payments_api'),
    path('api/payments/<int:payment_id>/', views.payment_api, name='payment_api'),
    path('api/coupons/', views.coupons_api, name='coupons_api'),
    path('api/coupons/<int:coupon_id>/', views.coupon_api, name='coupon_api'),
]
