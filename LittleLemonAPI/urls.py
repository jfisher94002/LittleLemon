from django.contrib import admin
from django.urls import path, include
from djoser.views import TokenCreateView

from .models import MenuItem, Cart, Order, OrderItem, Category
from . import views
from .views import menu_items_list, CustomView

urlpatterns = [
    #path('token/login/', include('djoser.urls')),
    #path('token/login/', TokenCreateView.as_view(), name='token_create'),

    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
#    path('menu/', views.menu, name='menu'),
#    path('book/', views.books, name='book'),   
    path('menu-items', views.menu_items, name="menu_items"),
#    path('menu-items', menu_items_list, name="menu_items_list"),
#    path('menu-items/<int:pk>/', CustomView.as_view(), name="display_menu_item"),
]