from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    cuisine = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, default="https://images.unsplash.com/photo-1504674900247-0877df9cc836")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)
    delivery_time = models.CharField(max_length=50)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, default="https://images.unsplash.com/photo-1546069901-ba9599a7e63c")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name