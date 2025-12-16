from datetime import date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Menu, MenuItem, FoodItem
from .serializers import MenuItemSerializer

class TodayMenuView(APIView):
    def get(self, request):
        today = date.today()
        menu_items = MenuItem.objects.filter(menu__date=today)
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)


class FastMenuView(APIView):
    def get(self, request):
        today = date.today()
        menu_items = MenuItem.objects.filter(
            menu__date=today,
            food_item__is_fast=True
        )
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)
