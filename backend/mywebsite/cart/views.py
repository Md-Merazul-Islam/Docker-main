from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product, Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewsSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewsSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Ensure a Cart exists for the user, or create one
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Retrieve the Product and Quantity from the request data
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        quantity = request.data.get('quantity', 1)

        # Create or update the CartItem
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, product=product)
        cart_item.quantity = quantity if item_created else cart_item.quantity + quantity
        cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart_item.quantity = request.data.get('quantity', cart_item.quantity)
        cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart_item.delete()
        return Response({'message': 'Cart item removed successfully'}, status=status.HTTP_204_NO_CONTENT)
