

from django.urls import path
from .views import CheckOutView, payment_success_view, payment_failure_view

urlpatterns = [
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('success/', payment_success_view, name='payment_success'),
    path('fail/', payment_failure_view, name='payment_failure'),
]
