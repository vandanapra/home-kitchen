from rest_framework import serializers
from .models import User, OTP

class SendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'mobile', 'email', 'role',
            'city', 'address', 'country', 'pincode'
        )

class SignupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=3, required=True)
    city = serializers.CharField(min_length=2, required=True)
    address = serializers.CharField(min_length=10, required=True)
    pincode = serializers.CharField(min_length=6, max_length=6, required=True)

    class Meta:
        model = User
        fields = ["name", "city", "address", "pincode"]

    def validate_pincode(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Pincode must be numeric")
        return value
