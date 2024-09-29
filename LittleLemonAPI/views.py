from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.core.cache import cache

# Create your views here.
from .models import MenuItem, Book
from .permissions import IsManager, IsDeliveryCrew
from .serializers import MenuItemSerializer

cache.clear()

#@api_view(['GET'])
#@authentication_classes([TokenAuthentication])
#def authenticated_view(request):
    # Logic for authenticated view
#    ...
    
#@api_view(['GET'])
#@permission_classes([IsAuthenticated, IsManager])
#def managers_only_view(request):
    # Logic for managers-only view
#    ...

#@api_view(['GET'])
#@permission_classes([IsAuthenticated, IsDeliveryCrew])
#def delivery_crew_only_view(request):
    # Logic for delivery crew-only view
 
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price']

    def get_permissions(self):
        if(self.request.method=='GET'):
            return []

        return [IsAuthenticated()]

#@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
#def unauthorized(request, menuItem):
#    return Response(status=status.HTTP_403_FORBIDDEN)

class DenyAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise PermissionDenied("You are not authorized to perform this action.")
        return False
        #return True

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated, DenyAccessPermission])
def menu(request):
    if not IsManager and not IsDeliveryCrew and not IsCustomer:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    menu_data = MenuItem.objects.all()
    main_data = {
        "menu": menu_data
    }
    return render(request, 'menu.html', main_data)

@csrf_exempt
@api_view(['GET','POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DenyAccessPermission])
def menu_items(request):
    return Response(status=status.HTTP_403_UNAUTHORIZED)

@csrf_exempt
@api_view(['POST'])
def menu(request):
    if not IsManager:
        return status.HTTP_401_UNAUTHORIZED
    
    menu_data = MenuItem.objects.all()
    main_data = {
        "menu": menu_data
    }
    return render(request, 'menu.html', main_data)

@csrf_exempt
@api_view(['GET'])
def get_menu_item(request, menuItem):
    try:
        menu_item = MenuItem.objects.get(id=menuItem)
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@csrf_exempt
def display_menu_item(request, pk=None):
    if pk:
    # Create a variable menu_item and assign it the value of objects.get(pk=pk) 
    # which is called over the Menu model class .
        menu_item = MenuItem.objects.get(pk=pk)

    # else:
    else:
    # Assign an empty string to the variable menu_item
        menu_item = ''
    return render(request, 'menu_item.html', {'menu_item': menu_item})

@csrf_exempt
@api_view(['GET'])
def get_all_menu_items(request):
    menu_items = MenuItem.objects.all()
    serializer = MenuItemSerializer(menu_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def create_menu_item(request):
    serializer = MenuItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT', 'PATCH'])
def update_menu_item(request, menuItem):
    try:
        menu_item = MenuItem.objects.get(id=menuItem)
        serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['DELETE'])
def delete_menu_item(request, menuItem):
    try:
        menu_item = MenuItem.objects.get(id=menuItem)
        menu_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



@csrf_exempt
def menu_items_list(request):
    if not user_has_permission(request.user):
        raise PermissionDenied("You are not authorized to perform this action.")
    # Return the menu items as a JSON response
    return JsonResponse(menu_items, safe=False)

# Create your views here.
@csrf_exempt
class CustomView(View):
    def post(self, request, *args, **kwargs):
        return HttpResponseForbidden("403 Forbidden: Unauthorized")

    def put(self, request, *args, **kwargs):
        return HttpResponseForbidden("403 Forbidden: Unauthorized")

    def patch(self, request, *args, **kwargs):
        return HttpResponseForbidden("403 Forbidden: Unauthorized")

    def delete(self, request, *args, **kwargs):
        return HttpResponseForbidden("403 Forbidden: Unauthorized")

    def get(self, request, *args, **kwargs):
        # Handle GET request if needed
        pass

@csrf_exempt
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def about(request):
    return render(request, 'about.html')

@csrf_exempt
def menu(request):
    return render(request, 'menu.html')

# Create your views here.
@csrf_exempt
def books(request):
    if request.method == 'GET':
        books = Book.objects.all().values()
        return JsonResponse({"books":list(books)})
    elif request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        price = request.POST.get('price')
        book = Book(
            title = title,
            author = author,
            price = price
        )
        try:
            book.save()
        except IntegrityError:
            return JsonResponse({'error':'true','message':'required field missing'},status=400)

        return JsonResponse(model_to_dict(book), status=201)