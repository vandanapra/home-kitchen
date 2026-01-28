from django.urls import path
from .views import OrderCreateView,SellerOrdersView, OrderListView,OrderCreateWhatsappView,OrderHistoryView,OrderActionView,OrderDeliveredView, CustomerOrderDetailView
from .razor import *
urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('place/', OrderCreateWhatsappView.as_view(), name='order-createwhatsapp'),
    path('customer/', OrderListView.as_view(), name='order-list'),
    path("seller/", SellerOrdersView.as_view()),
    path("history/", OrderHistoryView.as_view()),
    path("orders/<int:order_id>/action/",OrderActionView.as_view(),name="order-action"),
    path("orders/<int:order_id>/deliver/",OrderDeliveredView.as_view(),name="order-delivered"),
    path("razorpay/create/", CreateRazorpayOrderView.as_view()),
    path("orders/<int:pk>/", CustomerOrderDetailView.as_view()),
]
