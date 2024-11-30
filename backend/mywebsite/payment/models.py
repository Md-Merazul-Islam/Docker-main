from django.db import models
from django.contrib.auth.models import User
from cart.models import Cart


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = sum(
                item.product.discount_price * item.quantity for item in self.cart.items.all()
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
