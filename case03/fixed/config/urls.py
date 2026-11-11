from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurants.urls')),
    path('orders/', include('orders.urls')),
    # Add built-in auth login/logout routes so 'logout' works everywhere
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='restaurant_list'), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='orders/login.html'), name='login'),
]