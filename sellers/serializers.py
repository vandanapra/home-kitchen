from rest_framework import serializers
from .models import SellerProfile

class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = [
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
