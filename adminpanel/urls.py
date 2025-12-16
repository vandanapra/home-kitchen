from django.urls import path
from .views import (
    AdminUserListView,
    AdminSellerApprovalView,
    AdminOrderListView,AdminTriggerSubscriptionOrdersView
)

urlpatterns = [
    path('users/', AdminUserListView.as_view()),
    path('seller/<int:seller_id>/approve/', AdminSellerApprovalView.as_view()),
    path('orders/', AdminOrderListView.as_view()),
    path('subscription/create-orders/', AdminTriggerSubscriptionOrdersView.as_view()),
]
