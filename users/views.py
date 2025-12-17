import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserProfileSerializer
from notifications.services import send_whatsapp_message

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
    
#OTP is sent via WhatsApp instead of SMS
class SendOTPViewviaWhatsapp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(mobile=mobile, otp=otp_code)

        message = (
            f"Your HomeKitchen OTP is {otp_code}.\n"
            "Do not share this OTP with anyone."
        )

        try:
            send_whatsapp_message(mobile, message)
            return Response(
                {"message": "OTP sent via WhatsApp"},
                status=200
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400
            )



class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        otp = serializer.validated_data['otp']

        otp_obj = OTP.objects.filter(
            mobile=mobile, otp=otp, is_used=False
        ).first()

        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        user, created = User.objects.get_or_create(
            mobile=mobile,
            defaults={"is_verified": True}
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
