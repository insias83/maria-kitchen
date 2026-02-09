from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('food/<int:pk>/', views.food_detail, name='food_detail'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart'),
    path('remove/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('update-cart/<int:food_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('signup/', views.signup, name='signup'),
    
    # Login/Logout (Template name check kar lena folder ke hisaab se)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]