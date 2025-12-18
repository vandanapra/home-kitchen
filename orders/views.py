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
    permission_classes = [IsCustomer]

    # def post(self, request):
    #     serializer = OrderSerializer(data=request.data,context={"request": request})
    #     serializer.is_valid(raise_exception=True)

    #     order = serializer.save()

    #     message = f"""
    #     🍱 Order Confirmed!
    #     Order ID: {order.id}
    #     Total: ₹{order.total_amount}
    #     Status: Pending
    #     """

    #     send_whatsapp_message(request.user.mobile, message)

    #     return Response({"message": "Order placed successfully"},data=serializer.data)
    def post(self, request):
        try:
            user = request.user
            seller_id = request.data.get("seller_id")
            items = request.data.get("items", [])

            if not seller_id or not items:
                return Response(
                    {"message": "Seller & items are required"},
                    status=400
                )

            seller = SellerProfile.objects.get(id=seller_id)

            today = timezone.now().date()

            # ❌ duplicate order protection
            if Order.objects.filter(
                customer=user,
                seller=seller,
                order_date=today
            ).exists():
                return Response(
                    {"message": "You already placed order today"},
                    status=400
                )

            total = Decimal("0.00")

            order = Order.objects.create(
                customer=user,
                seller=seller,
                total_amount=0,
                status="PENDING"
            )

            for item in items:
                menu_item = MenuItem.objects.get(
                    id=item["menu_item_id"]
                )
                qty = int(item.get("quantity", 1))

                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=qty
                )

                total += menu_item.price * qty

            order.total_amount = total
            order.save()
        #     message = f"""
        # 🍱 Order Confirmed!
        # Order ID: {order.id}
        # Total: ₹{order.total_amount}
        # Status: Pending
        # """

        #     send_whatsapp_message(request.user.mobile, message)

            return Response(
                {
                    "message": "Order placed successfully",
                    "order_id": order.id,
                    "total": total
                },
                status=201
            )

        except SellerProfile.DoesNotExist:
            return Response(
                {"message": "Invalid seller"},
                status=400
            )

        except MenuItem.DoesNotExist:
            return Response(
                {"message": "Invalid menu item"},
                status=400
            )

        except Exception as e:
            return Response(
                {"message": str(e)},
                status=500
            )
    
class SellerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            seller=request.user
        ).order_by("-created_at")

        from .serializers import OrderSerializer
        return Response(
            OrderSerializer(orders, many=True).data
        )




class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
