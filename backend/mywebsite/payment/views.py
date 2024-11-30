from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect,csrf_exempt


class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            order = serializer.save()  
            return Response({'message': 'Payment successful. Order marked as paid.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@csrf_protect  
def payment_success_view(request):
    """Handle successful payment."""
    if request.method == 'GET':
        return render(request, 'success.html', {})

@csrf_protect  
def payment_failure_view(request):
    """Handle failed payment."""
    if request.method == 'GET':
        return render(request, 'fail.html', {})
