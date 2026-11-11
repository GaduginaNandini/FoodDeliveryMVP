from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from restaurants.models import FoodItem
from .models import Order, OrderItem

def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})
    str_item_id = str(item_id)
    
    current_qty = 0
    if str_item_id in cart:
        val = cart[str_item_id]
        current_qty = val.get('quantity', 0) if isinstance(val, dict) else int(val)
            
    cart[str_item_id] = current_qty + 1
        
    request.session['cart'] = cart
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'restaurant_list'))

def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    str_item_id = str(item_id)
    
    if str_item_id in cart:
        val = cart[str_item_id]
        current_qty = val.get('quantity', 0) if isinstance(val, dict) else int(val)
        
        if current_qty > 1:
            cart[str_item_id] = current_qty - 1
        else:
            del cart[str_item_id]
            
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    updated_cart = {}
    
    for item_id, val in cart.items():
        try:
            food = FoodItem.objects.get(pk=int(item_id))
            quantity = val.get('quantity', 1) if isinstance(val, dict) else int(val)
            
            subtotal = food.price * quantity
            total_price += subtotal
            cart_items.append({
                'food': food,
                'quantity': quantity,
                'subtotal': subtotal
            })
            updated_cart[item_id] = quantity
        except FoodItem.DoesNotExist:
            continue
            
    request.session['cart'] = updated_cart
    request.session.modified = True
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')
        
    total_price = 0
    valid_cart = {}
    for item_id, val in cart.items():
        try:
            food = FoodItem.objects.get(pk=int(item_id))
            quantity = val.get('quantity', 1) if isinstance(val, dict) else int(val)
            total_price += food.price * quantity
            valid_cart[item_id] = quantity
        except FoodItem.DoesNotExist:
            continue
            
    if not valid_cart:
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('view_cart')
        
    if request.method == 'POST':
        # Safely create order without unexpected keyword arguments
        order = Order.objects.create(user=request.user)
        for item_id, quantity in valid_cart.items():
            food = FoodItem.objects.get(pk=int(item_id))
            try:
                OrderItem.objects.create(order=order, food_item=food, quantity=quantity, price=food.price)
            except TypeError:
                # Fallback if OrderItem fields differ
                OrderItem.objects.create(order=order, food_item=food, quantity=quantity)
        
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('order_history')
        
    return render(request, 'orders/checkout.html', {'total_price': total_price})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})