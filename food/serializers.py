from rest_framework import serializers
from .models import FoodItem, Menu, MenuItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'
