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
from .serializers import SellerOrderSerializer
from orders.utils.email import send_order_email_to_seller,send_invoice_email_to_customer

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
            day = request.data.get("day")  # 🔥 NEW

            if not seller_id or not items or not day:
                return Response(
                    {"message": "Seller, items & day required"},
                    status=400
                )

            seller = SellerProfile.objects.get(user__id=seller_id)

            order = Order.objects.create(
                customer=user,
                seller=seller,
                day=day,
                total_amount=0,
                status="PENDING",
                order_date=timezone.now().date()  
            )
            
            total = Decimal("0.00")

            for item in items:
                menu_item = MenuItem.objects.get(
                    id=item["menu_item_id"],
                    menu_day__seller=seller.user,
                    menu_day__day=day    # 🔥 DAY MATCH
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
            send_order_email_to_seller(
                seller.user.email,
                order
            )
            send_invoice_email_to_customer(order)

           
            return Response({"message": "Order placed",}, status=201)
        except SellerProfile.DoesNotExist:
            return Response({"error": "Seller not found"}, status=404)

        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found for selected day"}, status=400)

        except Exception as e:
            print("ORDER ERROR:", e)
            return Response({"error": "Something went wrong"}, status=500)
    
class SellerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        date = request.query_params.get("date")
        # 🔥 Ensure seller profile exists
        if not hasattr(user, "seller_profile"):
            return Response(
                {"message": "Seller profile not found"},
                status=400
            )

        seller_profile = user.seller_profile

        orders = Order.objects.filter(
            seller=seller_profile,
        )
        if date:
            orders = orders.filter(order_date=date)
        orders = orders.order_by("-created_at")

        serializer = SellerOrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class OrderActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        action = request.data.get("action")

        if action not in ["ACCEPT", "REJECT"]:
            return Response(
                {"message": "Invalid action"},
                status=400
            )

        try:
            order = Order.objects.get(id=order_id)

            # 🔒 Only seller can update their order
            if order.seller.user != request.user:
                return Response(
                    {"message": "Unauthorized"},
                    status=403
                )

            if order.status != "PENDING":
                return Response(
                    {"message": "Order already processed"},
                    status=400
                )

            order.status = "ACCEPTED" if action == "ACCEPT" else "REJECTED"
            order.save()

            return Response({
                "message": f"Order {order.status.lower()} successfully",
                "status": order.status
            })

        except Order.DoesNotExist:
            return Response(
                {"message": "Order not found"},
                status=404
            )


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.query_params.get("date")
        orders = Order.objects.filter(customer=request.user)
        if date:
            orders = orders.filter(order_date=date)
        orders = orders.order_by("-created_at")
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
            
class OrderDeliveredView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            # 🔒 Only seller of this order
            if order.seller.user != request.user:
                return Response(
                    {"message": "Unauthorized"},
                    status=403
                )

            if order.status != "ACCEPTED":
                return Response(
                    {"message": "Only accepted orders can be delivered"},
                    status=400
                )

            order.status = "DELIVERED"
            order.save()

            return Response({
                "message": "Order marked as delivered",
                "status": order.status
            })

        except Order.DoesNotExist:
            return Response(
                {"message": "Order not found"},
                status=404
            )

class DownloadInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            customer=request.user   # 🔒 security
        )

        pdf_buffer = generate_order_invoice_pdf(order)
        invoice_no = generate_invoice_number(order)

        response = HttpResponse(
            pdf_buffer,
            content_type="application/pdf"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{invoice_no}.pdf"'
        )
        return response
