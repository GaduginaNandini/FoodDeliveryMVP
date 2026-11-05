from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from restaurants.models import FoodItem
from .models import Order, OrderItem

# Auth Views
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('restaurant_list')
    else:
        form = UserCreationForm()
    return render(request, 'orders/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('restaurant_list')
    else:
        form = AuthenticationForm()
    return render(request, 'orders/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('restaurant_list')

# Cart & Checkout Views
def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)
    cart = request.session.get('cart', {})
    
    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] += 1
    else:
        cart[str(item_id)] = {
            'name': food_item.name,
            'price': float(food_item.price),
            'quantity': 1,
            'restaurant_id': food_item.restaurant.id
        }
    
    request.session['cart'] = cart
    return redirect('restaurant_detail', pk=food_item.restaurant.id)

def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'orders/cart.html', {'cart': cart, 'total': total})

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')
    
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            phone_number=phone_number,
            address=address,
            total_amount=total
        )
        
        for item_id, item_data in cart.items():
            food_item = FoodItem.objects.get(id=int(item_id))
            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            
        request.session['cart'] = {}
        return redirect('order_success', order_id=order.id)
        
    return render(request, 'orders/checkout.html', {'total': total})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/success.html', {'order': order})

@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})