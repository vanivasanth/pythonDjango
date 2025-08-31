from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    UserSerializer, CategorySerializer, MenuItemSerializer, 
    CartSerializer, OrderSerializer, OrderItemSerializer
)

# User group management endpoints
@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response({"message": "User added to Manager group"}, status=status.HTTP_201_CREATED)
    return Response({"message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def manager_user(request, userId):
    user = get_object_or_404(User, id=userId)
    managers = Group.objects.get(name='Manager')
    if user in managers.user_set.all():
        managers.user_set.remove(user)
        return Response({"message": "User removed from Manager group"})
    return Response({"message": "User not in Manager group"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delivery_crew(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        crew = Group.objects.get(name='Delivery crew')
        crew.user_set.add(user)
        return Response({"message": "User added to Delivery crew group"}, status=status.HTTP_201_CREATED)
    return Response({"message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delivery_crew_user(request, userId):
    user = get_object_or_404(User, id=userId)
    crew = Group.objects.get(name='Delivery crew')
    if user in crew.user_set.all():
        crew.user_set.remove(user)
        return Response({"message": "User removed from Delivery crew group"})
    return Response({"message": "User not in Delivery crew group"}, status=status.HTTP_400_BAD_REQUEST)

# Category endpoints
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

# Menu items endpoints
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['category']
    search_fields = ['title']
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

# Cart management endpoints
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        unit_price = menuitem.price
        price = quantity * unit_price
        serializer.save(user=self.request.user, unit_price=unit_price, price=price)
    
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Order management endpoints
class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)
        if not cart_items.exists():
            return Response({"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.price for item in cart_items)
        order = serializer.save(user=self.request.user, total=total)
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        
        cart_items.delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)
    
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        if 'delivery_crew' in request.data:
            # Only managers can assign delivery crew
            if not request.user.groups.filter(name='Manager').exists():
                return Response(
                    {"message": "Only managers can assign delivery crew"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            delivery_crew_id = request.data['delivery_crew']
            try:
                delivery_user = User.objects.get(id=delivery_crew_id)
                if not delivery_user.groups.filter(name='Delivery crew').exists():
                    return Response(
                        {"message": "User is not in Delivery crew group"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                order.delivery_crew = delivery_user
            except User.DoesNotExist:
                return Response(
                    {"message": "User not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if 'status' in request.data:
            # Only delivery crew can update status for their orders
            if not request.user.groups.filter(name='Delivery crew').exists() or order.delivery_crew != request.user:
                return Response(
                    {"message": "Only assigned delivery crew can update status"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            order.status = request.data['status']
        
        order.save()
        return Response(OrderSerializer(order).data)