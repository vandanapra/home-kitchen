from django.urls import path
from .views import SellerProfileView,SellerMenuView

urlpatterns = [
    path('profile/', SellerProfileView.as_view(), name='seller-profile'),
    path("menu/", SellerMenuView.as_view()),
]
