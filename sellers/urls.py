from django.urls import path
from .views import SellerProfileView,SellerMenuView,CustomerTodayMenuView

urlpatterns = [
    path('profile/', SellerProfileView.as_view(), name='seller-profile'),
    path("menu/", SellerMenuView.as_view()),
    path("customer/menu/<int:seller_id>/",CustomerTodayMenuView.as_view()),
]
