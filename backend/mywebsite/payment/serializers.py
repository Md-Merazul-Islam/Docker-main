import paypalrestsdk
from rest_framework import serializers
from .models import Order
from cart.models import Cart
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.conf import settings

# Initialize PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Use 'live' for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'cart', 'total_amount', 'created_at', 'paid']
        read_only_fields = ['total_amount', 'created_at', 'paid']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # Retrieve the user's cart
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            raise serializers.ValidationError({'message': 'Cart is empty'})

        # Calculate the total price
        total_price = sum(item.product.discount_price * item.quantity for item in cart.items.all())

        # Create the order
        order = Order.objects.create(
            user=user,
            cart=cart,
            total_amount=total_price
        )

        # Handle payment processing
        payment_url = self.process_payment(order)

        if payment_url:
            return payment_url  # Return the payment approval URL
        else:
            raise serializers.ValidationError({'message': 'Payment failed during checkout. Please try again.'})

    @staticmethod
    def process_payment(order):
        # Create a PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": f"{order.total_amount:.2f}",
                    "currency": "USD"
                },
                "description": f"Order #{order.id} payment."
            }],
            "redirect_urls": {
                "return_url": "http://127.0.0.1:8000/api/payment/success/",
                "cancel_url": "http://127.0.0.1:8000/api/payment/fail/"
            }
        })

        if payment.create():
            return payment.links[1].href  # Redirect to PayPal for payment approval
        else:
            print("Error while creating payment:")
            print(payment.error)  # Log error for debugging
            return None  # Indicate failure

    @staticmethod
    def send_order_confirmation_email(order):
        email_subject = _("Order Confirmation")
        email_body = render_to_string('order_confirmation_email.html', {
            'user': order.user,
            'product_names': [item.product.name for item in order.cart.items.all()],
            'paid_amount': order.total_amount,
            'paid_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        email = EmailMultiAlternatives(
            subject=email_subject,
            body=email_body,
            from_email='no-reply@example.com',
            to=[order.user.email]
        )
        email.attach_alternative(email_body, "text/html")

        email.send()

    @staticmethod
    def reset_cart(cart):
        cart.items.all().delete()
