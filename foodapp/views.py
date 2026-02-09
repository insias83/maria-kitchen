from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Food, Order, OrderItem, Category
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

# 1. HOME VIEW: Search aur Category Filter ke saath
def home(request):
    search_query = request.GET.get('search')
    category_id = request.GET.get('category')
    
    foods = Food.objects.filter(is_available=True)
    
    if search_query:
        foods = foods.filter(name__icontains=search_query)
    
    if category_id:
        foods = foods.filter(category_id=category_id)
        
    categories = Category.objects.all()
    
    context = {
        'foods': foods,
        'categories': categories
    }
    return render(request, 'home.html', context)

# 2. ADD TO CART: AJAX Support ke saath
def add_to_cart(request, food_id):
    cart = request.session.get('cart', {})
    
    if not isinstance(cart, dict):
        cart = {}
    
    food_id_str = str(food_id)
    cart[food_id_str] = cart.get(food_id_str, 0) + 1
    
    request.session['cart'] = cart
    request.session.modified = True 
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success', 
            'cart_count': sum(cart.values())
        })
    
    messages.success(request, "Item added to cart!")
    return redirect('home')

# 3. CART PAGE
def cart_page(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for food_id, quantity in cart.items():
        food = Food.objects.filter(id=food_id).first()
        if food:
            subtotal = food.price * quantity
            total += subtotal
            cart_items.append({'food': food, 'quantity': quantity, 'subtotal': subtotal})
            
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

# 4. REMOVE FROM CART
def remove_from_cart(request, food_id):
    cart = request.session.get('cart', {})
    food_id_str = str(food_id)
    if food_id_str in cart:
        del cart[food_id_str]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')

# 5. UPDATE QUANTITY (AJAX)
def update_cart_quantity(request, food_id, action):
    cart = request.session.get('cart', {})
    food_id_str = str(food_id)
    
    if food_id_str in cart:
        if action == 'plus':
            cart[food_id_str] += 1
        elif action == 'minus':
            cart[food_id_str] -= 1
            if cart[food_id_str] <= 0:
                del cart[food_id_str]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    total = 0
    current_subtotal = 0
    for f_id, qty in cart.items():
        f = Food.objects.get(id=f_id)
        total += float(f.price) * qty
        if f_id == food_id_str:
            current_subtotal = float(f.price) * qty

    return JsonResponse({
        'status': 'success',
        'quantity': cart.get(food_id_str, 0),
        'subtotal': round(current_subtotal, 2),
        'total': round(total, 2),
        'cart_count': sum(cart.values())
    })

# 6. CHECKOUT PAGE
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    cart_items = []
    total = 0
    for food_id, quantity in cart.items():
        food = Food.objects.filter(id=food_id).first()
        if food:
            total += food.price * quantity
            cart_items.append({'food': food, 'quantity': quantity})

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})

# 7. PLACE ORDER: Final Logic
def place_order(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        cart = request.session.get('cart', {})

        if not cart:
            return redirect('home')

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    customer_name=name,
                    phone=phone,
                    address=address,
                    status='Pending'
                )

                total_bill = 0
                for food_id, quantity in cart.items():
                    food = Food.objects.get(id=food_id)
                    total_bill += (food.price * quantity)
                    OrderItem.objects.create(
                        order=order, food=food, 
                        quantity=quantity, price_at_order=food.price
                    )

                order.total_price = total_bill
                order.save()

            request.session['cart'] = {}
            request.session.modified = True
            return render(request, 'success.html', {'order': order})

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('checkout')

    return redirect('home')

# 8. DASHBOARD & AUTH
@login_required(login_url='signup')
def customer_dashboard(request):
    # orders = Order.objects.filter(user=request.user).order_by('-order_time')
    # Sahi line:
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'orders': orders})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def food_detail(request, pk):
    food = get_object_or_404(Food, pk=pk)
    return render(request, 'food_detail.html', {'food': food})