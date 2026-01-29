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

    # 🔹 GET menu (by date)
    def get(self, request):
        try:
            day = request.query_params.get("day")
            if not day:
                day = timezone.now().strftime("%A").upper()
            
            menu = MenuDay.objects.filter(
                seller=request.user,
                day=day
            ).first()

            if not menu:
                return Response({
                    "day": day,
                    "items": []
                })

            serializer = MenuDaySerializer(menu)
            data = serializer.data
            data["day"] = day
            return Response(data)
        except Exception as e:
            print (e)

    
    def put(self, request):
        try:
            # 🔹 DAY
            day = request.data.get("day")
            if not day:
                day = timezone.now().strftime("%A").upper()

            # 🔹 MULTIPART DATA
            names = request.data.getlist("name")
            descriptions = request.data.getlist("description")
            prices = request.data.getlist("price")
            ids = request.data.getlist("id")  # optional

            if not names:
                return Response(
                    {"error": "Items required"},
                    status=400
                )

            menu_day, created = MenuDay.objects.update_or_create(
                seller=request.user,
                day=day,
                defaults={"is_active": True}
            )

            existing_ids = []

            for i in range(len(names)):
                item_id = ids[i] if i < len(ids) else None
                image = request.FILES.get(f"image_{i}")  # 🔥 IMAGE

                # ✏️ UPDATE EXISTING ITEMേഴ
                if item_id:
                    menu_item = MenuItem.objects.filter(
                        id=item_id,
                        menu_day=menu_day
                    ).first()

                    if menu_item:
                        menu_item.name = names[i]
                        menu_item.description = descriptions[i]
                        menu_item.price = prices[i]

                        # 🔥 IMAGE UPDATE (ONLY IF PROVIDED)
                        if image:
                            menu_item.image = image

                        menu_item.save()
                        existing_ids.append(menu_item.id)

                # ➕ ADD NEW ITEM
                else:
                    new_item = MenuItem.objects.create(
                        menu_day=menu_day,
                        name=names[i],
                        description=descriptions[i],
                        price=prices[i],
                        image=image,        # 🔥 IMAGE SAVED
                        is_available=True
                    )
                    existing_ids.append(new_item.id)

            return Response({
                "message": "Menu saved successfully",
                "day": day
            })

        except Exception as e:
            print("MENU ERROR:", e)
            return Response(
                {"error": "Something went wrong"},
                status=500
            )



class CustomerTodayMenuView(APIView):
    permission_classes = []  # Public API

    def get(self, request, seller_id):
        # today = timezone.now().date()
        try:
            day = request.query_params.get("day")
            if not day:
                day = timezone.now().strftime("%A").upper()

            menu = MenuDay.objects.filter(
                seller_id=seller_id,
                day=day,
                is_active=True
            ).first()

            if not menu:
                return Response({
                    "message": "No menu available today"
                }, status=200)

            serializer = MenuDaySerializer(menu, context={"request": request})
            data = serializer.data
            data["day"] = day
            return Response(data)
        except Exception as e:
            print (e)
    


class CustomerSellerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sellers = SellerProfile.objects.filter(
            is_active=True,
            user__role="SELLER"
        ).select_related("user")

        data = SellerProfileSerializer(sellers, many=True).data
        return Response(data)
    
class SellerMenuItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = MenuItem.objects.get(
                id=item_id,
                menu_day__seller=request.user
            )
            item.delete()
            return Response({"message": "Item deleted"})
        except MenuItem.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=404
            )
            
            
class CustomerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        data = []

        sellers = SellerProfile.objects.filter(is_active=True)

        for seller in sellers:
            menu = MenuDay.objects.filter(
                seller=seller.user,
                date=today
            ).first()

            data.append({
                "seller_id": seller.user.id,
                "kitchen_name": seller.kitchen_name,
                "description": seller.description,
                "menu": MenuDaySerializer(menu).data if menu else None
            })

        return Response(data)
    
