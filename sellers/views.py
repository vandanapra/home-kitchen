from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SellerProfile
from .serializers import SellerProfileSerializer
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
        serializer = SellerProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile, created = SellerProfile.objects.update_or_create(
            user=request.user,
            defaults=serializer.validated_data
        )

        return Response({
            "message": "Kitchen profile saved successfully"
        })
