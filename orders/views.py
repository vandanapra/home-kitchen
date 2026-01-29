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
from .serializers import SellerOrderSerializer,CustomerOrderSerializer
from orders.utils.email import send_order_email_to_seller,send_invoice_email_to_customer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from users.models import UserAddress
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
            address_id = request.data.get("address_id")
            payment_method = request.data.get("payment_method", "COD")
            paid_amount = Decimal(request.data.get("paid_amount", 0))
            if not seller_id or not items or not day:
            # if not all([seller_id, items, day, address, city, pincode]):
                return Response(
                    {"message": "Seller, items & day required"},
                    status=400
                )

            seller = SellerProfile.objects.get(user__id=seller_id)
            if address_id:
                address = UserAddress.objects.get(
                    id=address_id,
                    user=user
                )
            else:
                address = UserAddress.objects.filter(
                    user=user,
                    is_default=True
                ).first()


            if not address:
                return Response(
                    {"error": "No default address set"},
                    status=400
                )

            order = Order.objects.create(
                customer=user,
                seller=seller,
                day=day,
                payment_method=payment_method,
                paid_amount=paid_amount,
                total_amount=0,
                status="PAID" if payment_method in ["ONLINE", "PARTIAL"] else "PENDING",
                order_date=timezone.now().date() ,
                delivery_address=address.address,
                delivery_city=address.city,
                delivery_pincode=address.pincode 
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

           
            return Response({"message": "Order placed", "order_id": order.id}, status=201)
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


class CustomerOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = Order.objects.filter(
            id=pk,
            customer=request.user
        ).first()

        if not order:
            return Response({"error": "Not found"}, status=404)

        serializer = CustomerOrderSerializer(order)
        return Response(serializer.data)

class OrderInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            customer=request.user
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        y = height - 50

        # ===== HEADER =====
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, y, "Home Kitchen Invoice")
        y -= 40

        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Invoice No: HK-{order.id}")
        y -= 15
        p.drawString(50, y, f"Order Date: {order.created_at.strftime('%d %b %Y')}")
        y -= 30

        # ===== CUSTOMER =====
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Customer Details")
        y -= 15

        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Name: {order.customer.name}")
        y -= 15
        p.drawString(50, y, f"Address: {order.delivery_address}")
        y -= 15
        p.drawString(50, y, f"{order.delivery_city} - {order.delivery_pincode}")
        y -= 30

        # ===== ORDER ITEMS =====
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Order Items")
        y -= 20

        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Item")
        p.drawString(300, y, "Qty")
        p.drawString(350, y, "Price")
        y -= 15

        p.setFont("Helvetica", 10)
        for item in order.items.all():
            p.drawString(50, y, item.menu_item.name)
            p.drawString(300, y, str(item.quantity))
            p.drawString(350, y, f"₹{item.menu_item.price}")
            y -= 15

        y -= 20

        # ===== TOTAL =====
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"Total Amount: ₹{order.total_amount}")
        y -= 15
        p.drawString(50, y, f"Payment Method: {order.payment_method}")
        y -= 15
        p.drawString(50, y, f"Paid Amount: ₹{order.paid_amount}")

        y -= 40

        p.setFont("Helvetica-Oblique", 9)
        p.drawString(50, y, "Thank you for ordering from Home Kitchen!")

        p.showPage()
        p.save()

        return response

