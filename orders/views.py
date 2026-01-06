from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from common.permissions import IsCustomer
from notifications.services import send_whatsapp_message
from decimal import Decimal
from django.utils import timezone
from .models import Order, OrderItem
from sellers.models import MenuItem, SellerProfile

class OrderCreateView(APIView):
    # permission_classes = [IsCustomer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=request.user, status="PENDING")
        return Response(serializer.data)
    
###order create thorough whatsappmessage   
class OrderCreateWhatsappView(APIView):
    # permission_classes = [IsCustomer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            seller_id = request.data.get("seller_id")
            items = request.data.get("items", [])

            if not seller_id or not items:
                return Response(
                    {"message": "Seller & items required"},
                    status=400
                )

            seller = SellerProfile.objects.get(user__id=seller_id)
            today = timezone.now().date()

            if Order.objects.filter(
                customer=user,
                seller=seller,
                order_date=today
            ).exists():
                return Response(
                    {"message": "Order already placed today"},
                    status=400
                )

            order = Order.objects.create(
                customer=user,
                seller=seller,
                total_amount=0,
                status="PENDING"
            )

            total = Decimal("0.00")

            for item in items:
                menu_item = MenuItem.objects.get(
                    id=item["menu_item_id"],
                    menu_day__seller=seller.user   # 🔥 IMPORTANT
                )

                qty = int(item["quantity"])

                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=qty
                )

                total += menu_item.price * qty

            order.total_amount = total
            order.save()

            return Response(
                {
                    "message": "Order placed successfully",
                    "order_id": order.id,
                    "total": total
                },
                status=201
            )
        except Exception as e:
            print(e)
    
class SellerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            seller=request.user
        ).order_by("-created_at")

        from .serializers import SellerOrderSerializer
        return Response(
            SellerOrderSerializer(orders, many=True).data
        )




class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = Order.objects.filter(
                customer=request.user
            ).order_by("-created_at")

            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(e)