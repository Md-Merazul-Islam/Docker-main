from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, TrendingProductsViewSet,LastProductsViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products-list', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('trending-products/', TrendingProductsViewSet.as_view({'get': 'list'}), name='trending-products'),
    path('recent-products/', LastProductsViewSet.as_view({'get': 'list'}), name='recent-products'),
]
