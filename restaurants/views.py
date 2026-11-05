from django.shortcuts import render, get_object_or_404
from .models import Restaurant, FoodItem

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    food_items = restaurant.food_items.all()
    return render(request, 'restaurants/restaurant_detail.html', {'restaurant': restaurant, 'food_items': food_items})