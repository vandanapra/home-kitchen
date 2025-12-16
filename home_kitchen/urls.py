from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('users.urls')),
    path('api/seller/', include('sellers.urls')),
    path('api/food/', include('food.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/reviews/', include('rating_reviews.urls')),
    path('api/subscriptions/', include('subscription.urls')),
    path('api/admin/', include('adminpanel.urls')),
]
