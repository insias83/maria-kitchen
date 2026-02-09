from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. CATEGORY MODEL
# ==========================================
class Category(models.Model):
    name = models.CharField(max_length=100)
    # Gol photo ya icon ke liye image field
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ==========================================
# 2. FOOD ITEM MODEL
# ==========================================
class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='food_images/')
    is_available = models.BooleanField(default=True)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==========================================
# 3. ORDER MODEL
# ==========================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    # User ke sath link kiya hai taaki Dashboard par orders dikhein
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


# ==========================================
# 4. ORDER ITEMS MODEL
# ==========================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    # Price save karna zaroori hai kyunki food price baad mein change ho sakta hai
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2) 

    def __str__(self):
        return f"{self.quantity} x {self.food.name if self.food else 'Removed Item'}"