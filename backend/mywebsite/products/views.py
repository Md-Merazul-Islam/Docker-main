# imports
from .serializers import ProductSerializer
from rest_framework.response import Response
import random
from rest_framework.viewsets import ViewSet
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .permissions import IsAdminUserOrReadOnly

# Define Product Filter
from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    # Filter by name (contains the search term)
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    # Filter by category id (matches exactly or contains the search term)
    category_name = filters.CharFilter(
        field_name='category__id', lookup_expr='icontains')

    # Filter by price range (greater than or equal to a value)
    min_price = filters.NumberFilter(
        field_name='real_price', lookup_expr='gte')  # Min price filter
    max_price = filters.NumberFilter(
        field_name='real_price', lookup_expr='lte')  # Max price filter

    # Custom filter for discount percentage range
    discount_range = filters.ChoiceFilter(choices=[
        ('0-10', '0%-10%'),
        ('10-20', '10%-20%'),
        ('20-30', '20%-30%'),
        ('30-40', '30%-40%'),
        ('40-50', '40%-50%'),
        ('50+', '50%+')
    ], method='filter_by_discount_range')

    class Meta:
        model = Product
        fields = ['name', 'category_name', 'min_price', 'max_price', 'discount_range']

    def filter_by_discount_range(self, queryset, name, value):
        if value:
            # Parse the discount range value (e.g., '10-20' or '50+')
            if value == '50+':
                return queryset.filter(discount__gte=50)
            else:
                min_discount, max_discount = map(int, value.split('-'))
                return queryset.filter(discount__gte=min_discount, discount__lte=max_discount)
        return queryset

class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

# Category ViewSet


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

# Product ViewSet with filtering and pagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    # pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class TrendingProductsViewSet(ViewSet):
    """
    ViewSet for trending products.
    """

    def list(self, request):
        """
        Returns up to 8 random products as trending.
        """
        all_products = Product.objects.all()  # Optionally, add a filter for trending status
        if not all_products.exists():
            return Response([])

        # Fetch up to 8 random products
        random_products = random.sample(
            list(all_products),
            min(len(all_products), 8)
        )

        # Use the ProductSerializer to serialize the data
        serializer = ProductSerializer(random_products, many=True)
        return Response(serializer.data)



class LastProductsViewSet(ViewSet):
  
    def list(self, request):
        """
        Returns the last 6 products added based on creation date or ID.
        """
        last_products = Product.objects.all().order_by('-id')[:6] 
        # If there are no products, return an empty list
        if not last_products.exists():
            return Response([])
        # Serialize the data
        serializer = ProductSerializer(last_products, many=True)
        return Response(serializer.data)
