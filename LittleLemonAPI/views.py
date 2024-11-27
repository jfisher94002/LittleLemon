from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.forms.models import model_to_dict
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt
from django.contrib.auth.models import User, Group

from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import Order, OrderItem, Cart, CartItem, MenuItem, Category, Rating
from .permissions import IsManager, IsDeliveryCrew
from .serializers import MenuItemSerializer, CategorySerializer, RatingSerializer, UserSerializer, OrderSerializer, CartItemSerializer
from .throttles import TenCallsPerMinute

import logging
from datetime import date

logger = logging.getLogger('LittleLemonAPI')
def test_logging():
    logger.debug("Views:This is a test log message")
    logger.info("Views:This is an info log message")
    logger.warning("Views:This is a warning log message")
    logger.error("Views:This is an error log message")
    logger.critical("Views:This is a critical log message")

test_logging()
#cache.clear()
    
def isManager(request):
    result = request.user.groups.filter(name='Manager').exists()
    print(f"isManager function called: {result}")  # Simple test log message
    return result
def isDeliveryCrew(request):
    result = request.user.groups.filter(name='DeliveryCrew').exists()
    print(f"isDeliveryCrew function called: {result}")  # Simple test log message
    return result
def isCustomer(request):
    result = request.user.groups.filter(name='Customer').exists()
    print(f"isCustomer function called: {result}")  # Simple test log message
    return result

@csrf_exempt
@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
#@permission_classes([IsAuthenticated])
def menu_items(request):
    logger.debug("menu_items function called")  # Simple test log message    
    print("menu_items function called")  # Simple test log message    
    logger.debug(f"menu_items request: {request.data}")  # Log the request data for debugging
    print(f"menu_items request: {request.data}")  # Log the request data for debugging
    try:
        if request.method == "GET": 
            items = MenuItem.objects.select_related('category').all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            if category_name:
                items = items.filter(category__title=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            serialized_items = MenuItemSerializer(items, many=True)
            return Response(serialized_items.data)
        
        if not isManager(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
    
        if request.method == "POST":
            logger.debug(f"POST request data: {request.data}")  # Log the request data for debugging
            print(f"POST request data: {request.data}")  # Log the request data for debugging
            #print(request.data)  # Print the request data for debugging
            serialized_item = MenuItemSerializer(data=request.data)
            logger.debug(f"POST after serializer call: {serialized_item}")  # Log the request data for debugging
            print(f"POST after serializer call: {serialized_item}")  # Log the request data for debugging
            
            if serialized_item.is_valid():
                serialized_item.save()
                return Response(serialized_item.data, status=status.HTTP_201_CREATED)
            else:
                logger.debug(f"Response data: Invalid serialization")  # Log the response data for debugging
                print(f"Response data: Invalid serialization {serialized_item.errors}")  # Log the response data for debugging
                return Response(serialized_item.errors, status=status.HTTP_400_BAD_REQUEST)    
        
        if request.method == "PUT":
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        #return Response(status=status.HTTP_403_UNAUTHORIZED)
        if request.method == "PATCH":
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        
        if request.method == "DELETE":
            item_id = request.data.get('id')
            item = get_object_or_404(MenuItem, id=item_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"menu-items:Error processing request: {e}")
        print(f"menu-items:Error processing request: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def single_item(request, id):
    if isManager(request) or isDeliveryCrew(request) or isCustomer(request):
        if request.method == "GET":
            item = get_object_or_404(MenuItem, pk=id)
            serialized_item = MenuItemSerializer(item)
            return Response(serialized_item.data)
        
    if not isManager(request):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "PUT":
        item = get_object_or_404(MenuItem, pk=id)
        #item = MenuItem.objects.get(pk=id)
        serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
        if serialized_item.is_valid(raise_exception=True):
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        return Response(serialized_item.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "PATCH":
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
        if serialized_item.is_valid(raise_exception=True):
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        return Response(serialized_item.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        item = get_object_or_404(MenuItem, pk=id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
    return Response(status=status.HTTP_404_NOT_FOUND)
 
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']
    ordering = ['price']
    
class MenuItemsViewSet(viewsets.ModelViewSet):
    #throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer    
    permission_classes = [IsAuthenticated]
    def get_throttles(self):
        if self.action == 'create':
            throttle_classes = [UserRateThrottle]
        else:
            throttle_classes = []
        return [throttle() for throttle in throttle_classes]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def managers_view(request):
    # Logic for managers-only view
    if request.user.groups.filter(name='Manager').exists():
        return Response({'message': 'This is a managers-only view!'})
    else:
        return Response({'message': 'You are not authorized to view this content!'}, status=status.HTTP_403_FORBIDDEN)

@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check_anon(request):
    # Logic for checking the throttle rate
    return Response({'message': 'This is an Anon Rate throttle check view!'})

@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    # Logic for checking the throttle rate
    return Response({'message': 'This is a User Rate throttle check view!'})
 
@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
     return Response({'message': 'This is a secret message!'})  

# Create your views here.
@api_view()
@permission_classes([IsAuthenticated])
def me(request):
    return Response(request.user.email)

@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def managers(request):
    if isDeliveryCrew(request) or isCustomer(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
   
    if request.method == 'GET':
        managers_group = Group.objects.get(name='Manager')
        managers = managers_group.user_set.all()
        serialized_managers = UserSerializer(managers, many=True)
        return Response(serialized_managers.data)
    
    if request.method == 'POST':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        managers_group = Group.objects.get(name='Manager')
        managers_group.user_set.add(user)
        return Response({'message': 'User added to manager group!'}, status=status.HTTP_201_CREATED)
    
    if request.method == 'DELETE':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        managers_group = Group.objects.get(name='Manager')
        managers_group.user_set.remove(user)
        return Response({'message': 'User removed from manager group!'})

    return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Invalid request method!'})
                         
@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    if not isManager(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
   
    if request.method == 'GET':
        managers_group = Group.objects.get(name='DeliveryCrew')
        managers = managers_group.user_set.all()
        serialized_managers = UserSerializer(managers, many=True)
        return Response(serialized_managers.data)
    
    if request.method == 'POST':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        managers_group = Group.objects.get(name='DeliveryCrew')
        managers_group.user_set.add(user)
        return Response({'message': 'User added to Delivery Crew group!'}, status=status.HTTP_201_CREATED)
    
    if request.method == 'DELETE':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        managers_group = Group.objects.get(name='DeliveryCrew')
        managers_group.user_set.remove(user)
        return Response({'message': 'User removed from DeliveryCrew group!'})
                         
    return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Invalid request method!'})

class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []

        return [IsAuthenticated()]

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    user = request.user
    cart = get_or_create_cart(user)

    if not isCustomer(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        cart_items = CartItem.objects.filter(cart=cart)
        serialized_cart_items = CartItemSerializer(cart_items, many=True)
        return Response(serialized_cart_items.data)

    if request.method == 'POST':
        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity', 1)

        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={'quantity': quantity, 'unit_price': menu_item.price, 'price': menu_item.price * quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serialized_cart_item = CartItemSerializer(cart_item)
        return Response(serialized_cart_item.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        menu_item_id = request.data.get('menu_item_id')
        cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=menu_item_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    cart = get_or_create_cart(user)
    menu_item_id = request.data.get('menu_item_id')
    quantity = request.data.get('quantity', 1)

    menu_item = MenuItem.objects.get(id=menu_item_id)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        defaults={'quantity': quantity, 'unit_price': menu_item.price, 'price': menu_item.price * quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    serialized_cart_item = CartItemSerializer(cart_item)
    return Response(serialized_cart_item.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    print(f"create_order:request: {request}")
    if isCustomer(request):
        user = request.user

        if request.method == 'GET':
            orders = Order.objects.filter(user=user)
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            cart_items = CartItem.objects.filter(cart__user=user)

            if not cart_items.exists():
                return Response({'error': 'No items in cart'}, status=status.HTTP_400_BAD_REQUEST)

            print(f"cart_items: {cart_items}")
            total_price = sum(item.menu_item.price * item.quantity for item in cart_items)
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                delivery_crew=None,  # Assuming no delivery crew assigned at creation
                status='Pending',  # Default status
                date=date.today()  # Current date
            )

            order_items = []
            for item in cart_items:
                order_item = OrderItem(
                    order=order,
                    menuitem=item.menu_item,  # Correct field name
                    quantity=item.quantity,
                    unit_price=item.menu_item.price,
                    price=item.menu_item.price * item.quantity
                )
                order_items.append(order_item)

            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()

            serialized_order = OrderSerializer(order)
            return Response(serialized_order.data, status=status.HTTP_201_CREATED)
    elif isDeliveryCrew(request):
        if request.method == 'GET':
            delivery_crew = request.user
            orders = Order.objects.filter(delivery_crew=delivery_crew)
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)
    elif isManager(request):
        if request.method == 'GET':
            orders = Order.objects.all()
            print(f"create_order:isManager:Get:orders: {orders}")
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)
    return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Invalid request method!'})

@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def order(request, id):
    if request.method == 'GET':
        order = get_object_or_404(Order, pk=id)
        if order.user != request.user and not isManager(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_200_OK)
    
    if request.method == 'PUT':
        order = get_object_or_404(Order, pk=id)
        print(f"order:PUT;user={order.user};request.user={request.user}")
        if not isManager(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        if 'delivery_crew' in data:
            try:
                delivery_crew = get_object_or_404(User, pk=data['delivery_crew'])
                order.delivery_crew = delivery_crew
            except User.DoesNotExist:
                return Response({'error': 'Invalid delivery crew ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'status' in data:
            valid_statuses = [0, 1]  # 0: out for delivery, 1: delivered
            if data['status'] in valid_statuses:
                order.status = 'Out for delivery' if data['status'] == 0 else 'Delivered'
            else:
                return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"order:PUT;order={order}")
        order.save()
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        order = get_object_or_404(Order, pk=id)
        if not isManager(request) and not isDeliveryCrew(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        if isManager(request):
            if 'delivery_crew' in data:
                try:
                    delivery_crew = get_object_or_404(User, pk=data['delivery_crew'])
                    order.delivery_crew = delivery_crew
                except User.DoesNotExist:
                    return Response({'error': 'Invalid delivery crew ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'status' in data:
            valid_statuses = [0, 1]  # 0: out for delivery, 1: delivered
            if data['status'] in valid_statuses:
                order.status = 'Out for delivery' if data['status'] == 0 else 'Delivered'
            else:
                return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.save()
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_200_OK)
    
    if request.method == 'DELETE':
        order = get_object_or_404(Order, pk=id)
        if not isManager(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
    return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Invalid request method!'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_item(request, id):
    order_item = get_object_or_404(OrderItem, pk=id)
    order = order_item.order

    if order.user != request.user and not isManager(request):
        return Response(status=status.HTTP_403_FORBIDDEN)

    data = request.data
    if 'quantity' in data:
        order_item.quantity = data['quantity']
    if 'price' in data:
        order_item.price = data['price']
    if 'unit_price' in data:
        order_item.unit_price = data['unit_price']

    order_item.save()
    serialized_order_item = OrderItemSerializer(order_item)
    return Response(serialized_order_item.data, status=status.HTTP_200_OK)

#### OBSOLETED CODE ####
#@csrf_exempt
#@api_view(['GET'])
#@permission_classes([IsAuthenticated, DenyAccessPermission])
#def menu(request):
#    if not IsManager and not IsDeliveryCrew and not IsCustomer:
#        return Response(status=status.HTTP_401_UNAUTHORIZED)
#    menu_data = MenuItem.objects.all()
#    main_data = {
#        "menu": menu_data
#    }
#    return render(request, 'menu.html', main_data)
#class CategoriesView(generics.ListCreateAPIView):
#    queryset = Category.objects.all()
#    serializer_class = CategorySerializer()

#class DenyAccessPermission(BasePermission):
#    def has_permission(self, request, view):
#        if not request.user.is_authenticated:
#            raise PermissionDenied("You are not authorized to perform this action.")
#        return False
#        #return True

#@csrf_exempt
#@api_view(['POST'])
#def menu(request):
#    if not IsManager:
 #       return status.HTTP_401_UNAUTHORIZED
    
#   menu_data = MenuItem.objects.all()
#    main_data = {
#        "menu": menu_data
#    }
#    return render(request, 'menu.html', main_data)

#@csrf_exempt
#@api_view(['GET'])
#def get_menu_item(request, menuItem):
#    try:
#        menu_item = MenuItem.objects.get(id=menuItem)
#        serializer = MenuItemSerializer(menu_item)
#        return Response(serializer.data, status=status.HTTP_200_OK)
#    except MenuItem.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)
    
#@csrf_exempt
#def display_menu_item(request, pk=None):
#    if pk:
    # Create a variable menu_item and assign it the value of objects.get(pk=pk) 
    # which is called over the Menu model class .
        #menu_item = MenuItem.objects.get(pk=pk)

    # else:
#    else:
    # Assign an empty string to the variable menu_item
#        menu_item = ''
#    return render(request, 'menu_item.html', {'menu_item': menu_item})

#@csrf_exempt
#@api_view(['GET'])
#def get_all_menu_items(request):
#    menu_items = MenuItem.objects.all()
#    serializer = MenuItemSerializer(menu_items, many=True)
#    return Response(serializer.data, status=status.HTTP_200_OK)

#@csrf_exempt
#@api_view(['POST'])
#def create_menu_item(request):
#    serializer = MenuItemSerializer(data=request.data)
#    if serializer.is_valid():
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_201_CREATED)
#    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#@csrf_exempt
#@api_view(['PUT', 'PATCH'])
#def update_menu_item(request, menuItem):
#    try:
#        menu_item = MenuItem.objects.get(id=menuItem)
#        serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_200_OK)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    except MenuItem.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)

#@csrf_exempt
#@api_view(['DELETE'])
#def delete_menu_item(request, menuItem):
#    try:
#        menu_item = MenuItem.objects.get(id=menuItem)
#        menu_item.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#    except MenuItem.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)

#@csrf_exempt
#def menu_items_list(request):
#    if not user_has_permission(request.user):
#        raise PermissionDenied("You are not authorized to perform this action.")
#    # Return the menu items as a JSON response
#    return JsonResponse(menu_items, safe=False)

# Create your views here.
#@csrf_exempt
#class CustomView(View):
#    def post(self, request, *args, **kwargs):
#        return HttpResponseForbidden("403 Forbidden: Unauthorized")
#
#    def put(self, request, *args, **kwargs):
#        return HttpResponseForbidden("403 Forbidden: Unauthorized")
#
#    def patch(self, request, *args, **kwargs):
#        return HttpResponseForbidden("403 Forbidden: Unauthorized")
#
#    def delete(self, request, *args, **kwargs):
#        return HttpResponseForbidden("403 Forbidden: Unauthorized")
#
#    def get(self, request, *args, **kwargs):
#        # Handle GET request if needed
#        pass
#
#@csrf_exempt
#def home(request):
#    return render(request, 'home.html')

#@csrf_exempt
#def about(request):
#    return render(request, 'about.html')

#@csrf_exempt
#def menu(request):
#    return render(request, 'menu.html')
