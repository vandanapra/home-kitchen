from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from common.permissions import IsCustomer
from notifications.services import send_whatsapp_message


class OrderCreateView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=request.user, status="PENDING")
        return Response(serializer.data)
    
###order create thorough whatsappmessage   
class OrderCreateWhatsappView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save(
            customer=request.user,
            status="PENDING"
        )

        message = f"""
        🍱 Order Confirmed!
        Order ID: {order.id}
        Total: ₹{order.total_amount}
        Status: Pending
        """

        send_whatsapp_message(request.user.mobile, message)

        return Response(serializer.data)



class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
