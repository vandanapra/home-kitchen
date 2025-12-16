from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SellerProfile
from .serializers import SellerProfileSerializer
from common.permissions import IsSeller

class SellerProfileView(APIView):
    permission_classes = [IsSeller]

    def get(self, request):
        profile = SellerProfile.objects.get(user=request.user)
        serializer = SellerProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        serializer = SellerProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)
