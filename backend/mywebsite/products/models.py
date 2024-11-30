from django.db import models
from django.utils.text import slugify
import random


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00)
    real_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    image = models.TextField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    recommended_products = models.ManyToManyField('self', blank=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        if self.discount > 0:
            self.discount_price = self.real_price * (1 - self.discount / 100)
        else:
            self.discount_price = self.real_price

        super().save(*args, **kwargs)

    def get_recommended_products(self, num_recommendations=3):
        same_category_products = Product.objects.filter(
            category=self.category).exclude(id=self.id)
        recommended = random.sample(list(same_category_products), min(
            len(same_category_products), num_recommendations))
        return recommended

    def __str__(self):
        return self.name
