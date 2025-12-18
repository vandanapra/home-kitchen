from django.urls import path
from .views import SellerProfileView,SellerMenuView,CustomerTodayMenuView,CustomerSellerListView

urlpatterns = [
    path('profile/', SellerProfileView.as_view(), name='seller-profile'),
    path("menu/", SellerMenuView.as_view()),
    path("customer/menu/<int:seller_id>/",CustomerTodayMenuView.as_view()),
    path("customer/sellers/",CustomerSellerListView.as_view()),
]

