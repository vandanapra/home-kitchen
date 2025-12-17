import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserProfileSerializer
from notifications.services import send_whatsapp_message
from twilio.rest import Client
from django.conf import settings

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(mobile=mobile, otp=otp_code)

        # 🔔 SMS / WhatsApp integration here
        print("OTP:", otp_code)

        return Response({"message": "OTP sent successfully"})
    

class SendOTPViewviaWhatsapp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            mobile = request.data.get("mobile")
            print("VERIFY SID =", settings.TWILIO_VERIFY_SERVICE_SID)

            if not mobile:
                return Response(
                    {"error": "Mobile number required"},
                    status=400
                )

            mobile = mobile[-10:]  # normalize

            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            # ✅ THIS IS WHERE YOUR CODE IS USED
            verification = client.verify.services(
                settings.TWILIO_VERIFY_SERVICE_SID
            ).verifications.create(
                # to=f"whatsapp:+91{mobile}",
                to=f"+91{mobile}",
                channel="sms"
            )

            return Response({
                "message": "OTP sent via WhatsApp",
                "status": verification.status  # usually "pending"
            })
        except Exception as e:
            print("TWILIO ERROR:", e)
            return Response(
                {"error": str(e)},
                status=500
            )

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            mobile = request.data.get("mobile")
            otp = request.data.get("otp")

            if not mobile or not otp:
                return Response({"error": "Mobile & OTP required"}, status=400)

            mobile = mobile[-10:]

            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            verification_check = client.verify.services(
                settings.TWILIO_VERIFY_SERVICE_SID
            ).verification_checks.create(
                to=f"+91{mobile}",   # ✅ SAME FORMAT
                code=otp
            )

            if verification_check.status != "approved":
                return Response({"error": "Invalid OTP"}, status=400)

            user, _ = User.objects.get_or_create(
                mobile=mobile,
                defaults={"is_verified": True}
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        except Exception as e:
            print("TWILIO ERROR:", e)
            return Response(
                {"error": str(e)},
                status=500
            )

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
