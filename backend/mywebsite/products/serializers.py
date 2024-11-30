
from rest_framework import serializers
from .models import Category, Product
from django.utils.text import slugify
import random


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

    def update(self, instance, validated_data):
        if 'name' in validated_data and validated_data['name'] != instance.name:
            instance.name = validated_data['name']
            instance.slug = slugify(instance.name)
        instance.save()
        return instance


class RecommendedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug',
                  'real_price', 'discount_price', 'image']


class ProductSerializer(serializers.ModelSerializer):
    recommended_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'slug', 'description', 'discount',
                  'real_price', 'discount_price', 'image', 'quantity', 'recommended_products']
        read_only_fields = ['slug', 'discount_price']

    def get_recommended_products(self, obj):
        same_category_products = Product.objects.filter(
            category=obj.category).exclude(id=obj.id)
        if not same_category_products.exists():
            return []

        recommended = random.sample(
            list(same_category_products), min(len(same_category_products), 5))
        return RecommendedProductSerializer(recommended, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'slug', 'description',
                  'discount', 'real_price', 'discount_price', 'image', 'quantity']
        read_only_fields = ['slug', 'discount_price']
