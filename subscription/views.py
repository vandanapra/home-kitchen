from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from common.permissions import IsSeller
from .models import Subscription, SubscriptionPlan
from .serializers import SubscriptionSerializer
from common.permissions import IsCustomer

class SubscriptionCreateView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        """
        Customer subscribes to a seller's plan
        """
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription = serializer.save(
            customer=request.user,
            status='ACTIVE'
        )

        return Response({
            "message": "Subscription created successfully",
            "subscription": SubscriptionSerializer(subscription).data
        })

#List Subscriptions (Customer)
class SubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Customer can see all active & past subscriptions
        """
        subscriptions = Subscription.objects.filter(
            customer=request.user
        ).order_by('-created_at')

        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

#Seller – View Subscribers (Important)
class SellerSubscriptionListView(APIView):
    
    permission_classes = [IsSeller]

    def get(self, request):
        """
        Seller can see who subscribed to their tiffin service
        """
        subscriptions = Subscription.objects.filter(
            seller__user=request.user,
            status='ACTIVE'
        )

        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
