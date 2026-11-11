from decimal import Decimal

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from restaurants.models import FoodItem
from .models import Order, OrderItem

MAX_QTY = 20  # equivalence class: valid quantity per item is 1..20
COUPONS = {
    'SAVE10': ('percent', Decimal('10')),  # 10 % off
    'FLAT5': ('flat', Decimal('5.00')),    # $5 off
}


def _qty(val):
    """Cart values may be a dict (old format) or an int (current format).
    Corrupt values count as 0; valid ones are clamped to 0..MAX_QTY (AI review R2)."""
    try:
        raw = val.get('quantity', 0) if isinstance(val, dict) else val
        return max(0, min(int(raw), MAX_QTY))
    except (TypeError, ValueError):
        return 0


def _cart_lines(cart):
    """Return (lines, subtotal, clean_cart) for the session cart; skips bad ids."""
    lines, subtotal, clean = [], Decimal('0.00'), {}
    for item_id, val in cart.items():
        try:
            food = FoodItem.objects.get(pk=int(item_id), is_available=True)
        except (FoodItem.DoesNotExist, ValueError):
            continue
        qty = _qty(val)
        if qty < 1:
            continue
        line_total = food.price * qty
        subtotal += line_total
        lines.append({'food': food, 'quantity': qty, 'subtotal': line_total})
        clean[item_id] = qty
    return lines, subtotal, clean


def discount_for(code, subtotal):
    """Discount amount for a coupon code (never more than the subtotal)."""
    rule = COUPONS.get((code or '').strip().upper())
    if not rule:
        return Decimal('0.00')
    kind, value = rule
    amount = subtotal * value / 100 if kind == 'percent' else value
    return min(amount.quantize(Decimal('0.01')), subtotal)


def add_to_cart(request, item_id):
    food = get_object_or_404(FoodItem, pk=item_id, is_available=True)
    cart = request.session.get('cart', {})
    key = str(food.pk)
    cart[key] = min(_qty(cart.get(key, 0)) + 1, MAX_QTY)
    request.session['cart'] = cart
    request.session.modified = True
    referer = request.META.get('HTTP_REFERER', '')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        return redirect(referer)               # AI review R3b: no open redirect
    return redirect('restaurant_list')


def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    key = str(item_id)
    if key in cart:
        qty = _qty(cart[key])
        if qty > 1:
            cart[key] = qty - 1
        else:
            del cart[key]
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon', '').strip().upper()
        if code in COUPONS:
            request.session['coupon'] = code
            request.session.pop('coupon_error', None)
        else:
            request.session.pop('coupon', None)
            request.session['coupon_error'] = 'Invalid coupon code'
    return redirect('view_cart')


def view_cart(request):
    lines, subtotal, clean = _cart_lines(request.session.get('cart', {}))
    request.session['cart'] = clean
    code = request.session.get('coupon')
    discount = discount_for(code, subtotal)
    context = {
        'cart_items': lines,
        'subtotal': subtotal,
        'discount': discount,
        'coupon': code,
        'coupon_error': request.session.pop('coupon_error', None),
        'total_price': subtotal - discount,
    }
    return render(request, 'orders/cart.html', context)


@login_required
def checkout(request):
    lines, subtotal, clean = _cart_lines(request.session.get('cart', {}))
    if not clean:
        request.session['cart'] = {}
        return redirect('view_cart')
    discount = discount_for(request.session.get('coupon'), subtotal)
    total = subtotal - discount

    if request.method == 'POST':
        name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        if not (name and phone and address):
            return render(request, 'orders/checkout.html',
                          {'total': total, 'total_price': total,
                           'error': 'All delivery fields are required'}, status=400)
        with transaction.atomic():             # AI review R1: all-or-nothing
            order = Order.objects.create(user=request.user, full_name=name,
                                         phone_number=phone, address=address,
                                         total_amount=total)
            for line in lines:
                OrderItem.objects.create(order=order, food_item=line['food'],
                                         quantity=line['quantity'], price=line['food'].price)
        request.session['cart'] = {}
        request.session.pop('coupon', None)
        return redirect('order_history')
    return render(request, 'orders/checkout.html', {'total': total, 'total_price': total})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.save())
        return redirect('restaurant_list')
    return render(request, 'orders/register.html', {'form': form})
