from django.contrib import admin
from django.urls import path, include
from djoser.views import TokenCreateView
from rest_framework.authtoken.views import obtain_auth_token

from .models import MenuItem, Cart, Order, OrderItem
from . import views
#from .views import menu_items_list, CustomView

urlpatterns = [
    path('menu-items/', views.menu_items, name="menu_items"),
    path('menu-items/<int:id>', views.single_item, name="get-menu-item"),
    path('secret/', views.secret, name='secret'),  # Ensure this line defines the correct path
    path('manager-view/', views.managers_view, name='managers_view'),
    #path('roles', views.roles, name='roles'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    #path('throttle-check', views.throttle_check, name='throttle_check'),
    path('throttle-check-anon/', views.throttle_check_anon, name='throttle_check_anon'),
    path('throttle-check-auth/', views.throttle_check_auth, name='throttle_check_auth'),
    path('me', views.me, name='me'),
    path('groups/manager/users',views.managers),
    path('groups/delivery-crew/users',views.delivery_crew),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/menu-items', views.cart_menu_items, name='cart_menu_items'),
    path('orders/', views.create_order, name='create_order'),
    path('orders/<int:id>', views.order, name='order'),
    path('order-items/<int:id>', views.update_order_item, name='update_order_item'),
    #path('home/', views.home, name='home'),
    #path('about/', views.about, name='about'),
    path('ratings', views.RatingsView.as_view()),
]