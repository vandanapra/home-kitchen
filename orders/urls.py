from django.urls import path
from .views import OrderCreateView, OrderListView,OrderCreateWhatsappView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('create-whatsapp/', OrderCreateWhatsappView.as_view(), name='order-createwhatsapp'),
    path('list/', OrderListView.as_view(), name='order-list'),
]
