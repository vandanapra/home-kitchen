from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SellerProfile
from .serializers import *
from common.permissions import IsSeller
    

class SellerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsSeller]
    

    def get(self, request):
        profile = SellerProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({}, status=200)

        serializer = SellerProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = SellerProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            profile, created = SellerProfile.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data
            )

            return Response({
                "message": "Kitchen profile saved successfully"
            })
        except Exception as e:
            print(str(e))
            
class SellerMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        menu = MenuDay.objects.filter(
            seller=request.user,
            date=today
        ).first()

        if not menu:
            return Response({"menu": None})

        return Response(MenuDaySerializer(menu).data)

    def post(self, request):
        serializer = MenuDaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(seller=request.user)
        return Response({"message": "Menu saved successfully"})
