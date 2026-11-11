from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, FoodItem

class Command(BaseCommand):
    help = 'Seeds 10 restaurants with images and menu items'

    def handle(self, *args, **kwargs):
        FoodItem.objects.all().delete()
        Restaurant.objects.all().delete()

        restaurants_data = [
            {
                "name": "Burger Joint",
                "description": "Juicy gourmet burgers and crispy golden fries.",
                "cuisine": "Fast Food",
                "address": "123 Main St",
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
                "rating": 4.5,
                "delivery_time": "25-35 mins",
                "items": [
                    {"name": "Cheeseburger", "description": "Beef patty with melted cheddar", "price": 8.99, "category": "Burgers", "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd"},
                    {"name": "Crispy Fries", "description": "Golden salted fries", "price": 3.99, "category": "Sides", "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877"}
                ]
            },
            {
                "name": "Pizza Palace",
                "description": "Authentic wood-fired Italian pizzas.",
                "cuisine": "Italian",
                "address": "456 Oak Ave",
                "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
                "rating": 4.7,
                "delivery_time": "30-40 mins",
                "items": [
                    {"name": "Margherita Pizza", "description": "Fresh mozzarella and basil", "price": 12.99, "category": "Pizza", "image_url": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143"},
                    {"name": "Pepperoni Pizza", "description": "Loaded with spicy pepperoni", "price": 14.99, "category": "Pizza", "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e"}
                ]
            },
            {
                "name": "Sushi Express",
                "description": "Fresh rolls and traditional Japanese sashimi.",
                "cuisine": "Japanese",
                "address": "789 Pine Rd",
                "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c",
                "rating": 4.8,
                "delivery_time": "35-45 mins",
                "items": [
                    {"name": "Salmon Roll", "description": "Fresh salmon and avocado", "price": 11.99, "category": "Sushi", "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c"},
                    {"name": "California Roll", "description": "Crab, avocado, and cucumber", "price": 9.99, "category": "Sushi", "image_url": "https://images.unsplash.com/photo-1611143669185-af224c5e3252"}
                ]
            },
            {
                "name": "Taco Fiesta",
                "description": "Authentic street tacos and zesty salsas.",
                "cuisine": "Mexican",
                "address": "321 Elm St",
                "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47",
                "rating": 4.3,
                "delivery_time": "20-30 mins",
                "items": [
                    {"name": "Carne Asada Taco", "description": "Grilled steak with cilantro", "price": 3.50, "category": "Tacos", "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47"},
                    {"name": "Chicken Quesadilla", "description": "Melty cheese and shredded chicken", "price": 8.50, "category": "Mains", "image_url": "https://images.unsplash.com/photo-1618046582548-52d0bd675b48"}
                ]
            },
            {
                "name": "Dragon Wok",
                "description": "Flavorsome stir-fries and dim sum.",
                "cuisine": "Chinese",
                "address": "654 Maple Dr",
                "image_url": "https://images.unsplash.com/photo-1526318896980-cf78c08b2474",
                "rating": 4.4,
                "delivery_time": "25-35 mins",
                "items": [
                    {"name": "Kung Pao Chicken", "description": "Spicy diced chicken with peanuts", "price": 10.99, "category": "Mains", "image_url": "https://images.unsplash.com/photo-1526318896980-cf78c08b2474"},
                    {"name": "Veggie Spring Rolls", "description": "Crispy rolls with sweet chili", "price": 5.00, "category": "Appetizers", "image_url": "https://images.unsplash.com/photo-1541658016709-82535e94bc69"}
                ]
            },
            {
                "name": "Spice Route",
                "description": "Rich curries and tandoori specialties.",
                "cuisine": "Indian",
                "address": "987 Cedar Ln",
                "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0",
                "rating": 4.6,
                "delivery_time": "30-45 mins",
                "items": [
                    {"name": "Butter Chicken", "description": "Tender chicken in tomato cream sauce", "price": 13.99, "category": "Curry", "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0"},
                    {"name": "Garlic Naan", "description": "Tandoori flatbread with garlic", "price": 3.00, "category": "Breads", "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950"}
                ]
            },
            {
                "name": "Green Leaf Salads",
                "description": "Healthy, organic bowls and fresh juices.",
                "cuisine": "Healthy",
                "address": "111 Birch St",
                "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
                "rating": 4.2,
                "delivery_time": "15-25 mins",
                "items": [
                    {"name": "Caesar Salad", "description": "Romaine, parmesan, croutons", "price": 8.99, "category": "Salads", "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"},
                    {"name": "Green Detox Juice", "description": "Kale, apple, cucumber, lemon", "price": 5.99, "category": "Beverages", "image_url": "https://images.unsplash.com/photo-1610970881699-44a5587cabec"}
                ]
            },
            {
                "name": "Sweet Tooth Bakery",
                "description": "Artisanal pastries, cakes, and coffee.",
                "cuisine": "Bakery",
                "address": "222 Market St",
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff",
                "rating": 4.9,
                "delivery_time": "15-25 mins",
                "items": [
                    {"name": "Chocolate Croissant", "description": "Flaky butter pastry with chocolate", "price": 4.50, "category": "Pastries", "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a"},
                    {"name": "Red Velvet Cupcake", "description": "Classic cake with cream cheese frosting", "price": 3.75, "category": "Cakes", "image_url": "https://images.unsplash.com/photo-1587314168485-3236d6710814"}
                ]
            },
            {
                "name": "BBQ Smokehouse",
                "description": "Slow-cooked ribs and pulled pork sandwiches.",
                "cuisine": "Barbecue",
                "address": "333 River Rd",
                "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
                "rating": 4.7,
                "delivery_time": "35-50 mins",
                "items": [
                    {"name": "Pulled Pork Sandwich", "description": "Smoky pork with coleslaw", "price": 10.50, "category": "Sandwiches", "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1"},
                    {"name": "Beef Brisket Plate", "description": "Sliced brisket with BBQ sauce", "price": 16.99, "category": "Mains", "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947"}
                ]
            },
            {
                "name": "Mediterranean Olive",
                "description": "Fresh gyros, falafel, and hummus platters.",
                "cuisine": "Mediterranean",
                "address": "444 Coast Hwy",
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947",
                "rating": 4.5,
                "delivery_time": "25-35 mins",
                "items": [
                    {"name": "Lamb Gyro Wrap", "description": "Lamb, tzatziki, lettuce in pita", "price": 9.50, "category": "Wraps", "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba"},
                    {"name": "Hummus & Pita", "description": "Chickpea dip with olive oil", "price": 6.00, "category": "Appetizers", "image_url": "https://images.unsplash.com/photo-1577805947697-89e18249d767"}
                ]
            },
        ]

        for r_data in restaurants_data:
            items = r_data.pop("items")
            restaurant = Restaurant.objects.create(**r_data)
            for item in items:
                FoodItem.objects.create(restaurant=restaurant, **item)

        self.stdout.write(self.style.SUCCESS("Successfully seeded 10 restaurants with stunning images!"))