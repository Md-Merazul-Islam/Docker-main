
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Django REST Framework built-in login and logout views

    # extra app urls
    path('user/', include('users.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('payment/', include('payment.urls')),

    path('api-auth/', include('rest_framework.urls')),



]
