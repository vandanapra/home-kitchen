from django.urls import path
from .views import TodayMenuView, FastMenuView

urlpatterns = [
    path('menu/today/', TodayMenuView.as_view(), name='today-menu'),
    path('menu/fast/', FastMenuView.as_view(), name='fast-menu'),
]
