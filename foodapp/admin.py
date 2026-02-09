from django.contrib import admin
from .models import Category, Food, Order, OrderItem

admin.site.register(Category)
admin.site.register(Food)
admin.site.register(Order)
admin.site.register(OrderItem)