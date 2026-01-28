from django.urls import path
from .views import SellerProfileView,SellerMenuView,CustomerTodayMenuView,CustomerSellerListView,SellerMenuItemDeleteView,CustomerDashboardView,OrderInvoiceView

urlpatterns = [
    path('profile/', SellerProfileView.as_view(), name='seller-profile'),
    path("menu/", SellerMenuView.as_view()),
    path("customer/menu/<int:seller_id>/",CustomerTodayMenuView.as_view()),
    path("customer/sellers/",CustomerSellerListView.as_view()),
    path("menu/item/<int:item_id>/",SellerMenuItemDeleteView.as_view()),
    path("customer/dashboard/", CustomerDashboardView.as_view()),
    path("invoice/<int:order_id>/",OrderInvoiceView.as_view()
),
]

