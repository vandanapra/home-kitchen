from rest_framework import serializers
from .models import *

class SellerProfileSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(source="user.id", read_only=True)
    class Meta:
        model = SellerProfile
        fields = ["id",
            "seller_id",
            "kitchen_name",
            "description",
            "opening_time",
            "closing_time",
            "is_active",
        ]

    def validate(self, data):
        if data["opening_time"] >= data["closing_time"]:
            raise serializers.ValidationError(
                "Opening time must be before closing time"
            )
        return data
    
class MenuItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price", "is_available","image_url"]
    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url 


class MenuDaySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuDay
        fields = ["id", "day", "is_active", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        menu_day = MenuDay.objects.create(**validated_data)

        for item in items_data:
            MenuItem.objects.create(menu_day=menu_day, **item)

        return menu_day
