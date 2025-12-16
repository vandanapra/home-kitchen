from django.urls import path
from .views import (
    SubscriptionCreateView,
    SubscriptionListView,
    SellerSubscriptionListView
)

urlpatterns = [
    path('create/', SubscriptionCreateView.as_view(), name='subscription-create'),
    path('list/', SubscriptionListView.as_view(), name='subscription-list'),
    path('seller/list/', SellerSubscriptionListView.as_view(), name='seller-subscriptions'),
]
