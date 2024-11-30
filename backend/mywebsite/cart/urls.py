from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewsSet, CartItemViewsSet

router = DefaultRouter()
router.register(r'cart', CartViewsSet, basename='cart')
router.register(r'cart-items', CartItemViewsSet, basename='cartitem')
# urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]

""""

POST / api/cart-items/

{
    "product_id": 1,
    "quantity": 2
}


check out : 
    
{
    "user":7,
    "cart":1
}
"""
