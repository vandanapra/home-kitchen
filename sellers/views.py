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
        today = timezone.now().date()

        items = request.data.get("items", [])

        # ✅ FIX: update_or_create instead of create
        menu_day, created = MenuDay.objects.update_or_create(
            seller=request.user,
            date=today,
            defaults={
                "is_active": True
            }
        )

        # 🔥 IMPORTANT: old items delete karo
        menu_day.items.all().delete()

        # 🔥 new items add karo
        for item in items:
            MenuItem.objects.create(
                menu_day=menu_day,
                name=item.get("name"),
                description=item.get("description", ""),
                price=item.get("price"),
                is_available=True
            )

        return Response({
            "message": "Menu saved successfully",
            "created": created
        })


class CustomerTodayMenuView(APIView):
    permission_classes = []  # Public API

    def get(self, request, seller_id):
        today = timezone.now().date()

        menu = MenuDay.objects.filter(
            seller_id=seller_id,
            date=today,
            is_active=True
        ).first()

        if not menu:
            return Response({
                "message": "No menu available today"
            }, status=200)

        serializer = MenuDaySerializer(menu)
        return Response(serializer.data)
    
class CustomerSellerListView(APIView):
    permission_classes = []  # public API

    def get(self, request):
        sellers = SellerProfile.objects.filter(is_active=True)

        data = []
        for seller in sellers:
            data.append({
                "id": seller.user.id,                 # 🔑 IMPORTANT
                "kitchen_name": seller.kitchen_name,
                "description": seller.description,
                "avg_rating": seller.avg_rating,
                "opening_time": seller.opening_time,
                "closing_time": seller.closing_time,
            })

        return Response(data)