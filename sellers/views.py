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
            
# class SellerMenuView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         today = timezone.now().date()
#         menu = MenuDay.objects.filter(
#             seller=request.user,
#             date=today
#         ).first()

#         if not menu:
#             return Response({"menu": None})

#         return Response(MenuDaySerializer(menu).data)
    
#     def post(self, request):
#         today = timezone.now().date()

#         items = request.data.get("items", [])

#         # ✅ FIX: update_or_create instead of create
#         menu_day, created = MenuDay.objects.update_or_create(
#             seller=request.user,
#             date=today,
#             defaults={
#                 "is_active": True
#             }
#         )

#         # 🔥 IMPORTANT: old items delete karo
#         menu_day.items.all().delete()

#         # 🔥 new items add karo
#         for item in items:
#             MenuItem.objects.create(
#                 menu_day=menu_day,
#                 name=item.get("name"),
#                 description=item.get("description", ""),
#                 price=item.get("price"),
#                 is_available=True
#             )

#         return Response({
#             "message": "Menu saved successfully",
#             "created": created
#         })

class SellerMenuView(APIView):
    permission_classes = [IsAuthenticated]

    # 🔹 GET menu (by date)
    def get(self, request):
        date = request.query_params.get("date")
        date = date or timezone.now().date()

        menu = MenuDay.objects.filter(
            seller=request.user,
            date=date
        ).first()

        if not menu:
            return Response({"menu": None})

        return Response(MenuDaySerializer(menu).data)

    # 🔹 PUT = ADD + EDIT
    def put(self, request):
        try:
            date = request.data.get("date") or timezone.now().date()
            items = request.data.get("items", [])

            if not items:
                return Response(
                    {"error": "Items required"},
                    status=400
                )

            menu_day, created = MenuDay.objects.update_or_create(
                seller=request.user,
                date=date,
                defaults={"is_active": True}
            )

            existing_ids = []

            for item in items:
                item_id = item.get("id")

                # ✏️ UPDATE EXISTING ITEM
                if item_id:
                    menu_item = MenuItem.objects.filter(
                        id=item_id,
                        menu_day=menu_day
                    ).first()

                    if menu_item:
                        menu_item.name = item["name"]
                        menu_item.description = item.get("description", "")
                        menu_item.price = item["price"]
                        menu_item.save()
                        existing_ids.append(menu_item.id)

                # ➕ ADD NEW ITEM (APPEND)
                else:
                    new_item = MenuItem.objects.create(
                        menu_day=menu_day,
                        name=item["name"],
                        description=item.get("description", ""),
                        price=item["price"],
                        is_available=True
                    )
                    existing_ids.append(new_item.id)

            return Response({
                "message": "Menu updated successfully",
                "menu_id": menu_day.id
            })
        except Exception as e:
            print(e)


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
    
# class CustomerSellerListView(APIView):
#     permission_classes = []  # public API

#     def get(self, request):
#         sellers = SellerProfile.objects.filter(is_active=True)

#         data = []
#         for seller in sellers:
#             data.append({
#                 "id": seller.user.id,                 # 🔑 IMPORTANT
#                 "kitchen_name": seller.kitchen_name,
#                 "description": seller.description,
#                 "avg_rating": seller.avg_rating,
#                 "opening_time": seller.opening_time,
#                 "closing_time": seller.closing_time,
#             })

#         return Response(data)

class CustomerSellerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sellers = SellerProfile.objects.filter(
            is_active=True,
            user__role="Seller"
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
