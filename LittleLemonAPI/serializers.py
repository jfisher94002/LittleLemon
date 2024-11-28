from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator

from .models import MenuItem, Category, Rating, Order, OrderItem, CartItem
import logging

logger = logging.getLogger('LittleLemonAPI')
def test_logging():
    logger.debug("Serializer:This is a test log message")
    logger.info("Serializer:This is an info log message")
    logger.warning("Serializer:This is a warning log message")
    logger.error("Serializer:This is an error log message")
    logger.critical("Serializer:This is a critical log message")

test_logging()
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']   
        
class MenuItemSerializer(serializers.ModelSerializer):
    print("Entering MenuItemSerializer now data:")  # Log the validated data for debugging
    stock = serializers.IntegerField(source='inventory', required=False)
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_tax') 
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=True)
    print(f"MenuItemSerializer-stock:{stock}")  # Log the validated data for debugging
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'price_after_tax', 'inventory', 'stock', 'category', 'category_id']
        #fields = '__all__'

        extra_kwargs = {
            'price': {'min_value': Decimal('2.00')},
            'inventory':{'min_value':0}
        }
    
    logger.debug(f"Entering method now data: {stock}")  # Log the validated data for debugging
    print(f"Entering method now data: {stock}")  # Log the validated data for debugging
    def calculate_tax(self, product):
        logger.debug(f"Calculating price for product: {product}")
        print(f"Calculating price for product: {product}")
        price = product['price'] if isinstance(product, dict) else product.price
        return price * Decimal(1.1)
    
    def create(self, validated_data):
        print("MenuItemSerializer-created")
        logger.debug(f"MenuItemSerializer:Validated data in create method: {validated_data}")  # Log the validated data for debugging
        print(f"MenuItemSerializer:Validated data in create method: {validated_data}")  # Log the validated data for debugging
        category_id = validated_data.pop('category_id')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category with id {category_id} does not exist")
        menu_item = MenuItem.objects.create(category=category, **validated_data)
        logger.debug(f"Created MenuItem: {menu_item}")
        print(f"Created MenuItem: {menu_item}")
        return menu_item

    def update(self, instance, validated_data):
        print("MenuItemSerializer-update")
        category_id = validated_data.pop('category_id', None)
        if category_id:
            category = Category.objects.get(id=category_id)
            instance.category = category
        instance.title = validated_data.get('title', instance.title)
        instance.price = validated_data.get('price', instance.price)
        instance.inventory = validated_data.get('inventory', instance.inventory)
        instance.save()
        logger.debug(f"Updated MenuItem: {instance}")
        print(f"Updated MenuItem: {instance}")
        return instance
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class RatingSerializer (serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Rating
        fields = ['user', 'menuitem_id', 'rating']

        validators = [
            UniqueTogetherValidator(
                queryset=Rating.objects.all(),
                fields=['user', 'menuitem_id']
            )
        ]

        extra_kwargs = {
            'rating': {'min_value': 0, 'max_value':5},
        }

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_price', 'items']
        
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'menu_item', 'quantity', 'price']