from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsAdmin
from users.models import User
from sellers.models import SellerProfile
from orders.models import Order
from .serializers import (
    AdminUserSerializer,
    AdminSellerSerializer,
    AdminOrderSerializer
)
from subscription.services import create_daily_subscription_orders

##Admin – List All Users
class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)
    
#Admin – Approve / Block Seller
class AdminSellerApprovalView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, seller_id):
        seller = SellerProfile.objects.get(id=seller_id)
        seller.is_active = request.data.get('is_active', True)
        seller.save()

        return Response({
            "message": "Seller status updated",
            "is_active": seller.is_active
        })

#Admin – View All Orders
class AdminOrderListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        serializer = AdminOrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class AdminTriggerSubscriptionOrdersView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        create_daily_subscription_orders()
        return Response({"message": "Subscription orders created"})

