# views.py
import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = request.data.get("amount")

            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            print("RAZORPAY KEY ID:", settings.RAZORPAY_KEY_ID)
            print("RAZORPAY KEY SECRET:", settings.RAZORPAY_KEY_SECRET)

            order = client.order.create({
                "amount": int(float(amount) * 100),  # paise
                "currency": "INR",
                "payment_capture": 1,
            })

            return Response({
                "razorpay_order_id": order["id"],
                "key": settings.RAZORPAY_KEY_ID,
                "amount":amount
            })
        except Exception as e:
            print("RAZORPAY ERROR:", e)
            return Response(
                {"message": "Payment initiation failed"},
                status=500
            )                        
