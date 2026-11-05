from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.view_cart, name='view_cart'),
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('history/', views.order_history, name='order_history'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]