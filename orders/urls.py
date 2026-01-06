from django.urls import path
from .views import OrderCreateView,SellerOrdersView, OrderListView,OrderCreateWhatsappView,OrderHistoryView,OrderActionView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('place/', OrderCreateWhatsappView.as_view(), name='order-createwhatsapp'),
    path('customer/', OrderListView.as_view(), name='order-list'),
    path("seller/", SellerOrdersView.as_view()),
    path("history/", OrderHistoryView.as_view()),
    path(
    "orders/<int:order_id>/action/",
    OrderActionView.as_view(),
    name="order-action"
),
]
