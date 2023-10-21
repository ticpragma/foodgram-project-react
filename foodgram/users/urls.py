from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import DjoserUserViewSet

urlpatterns = [
    path('users/me/', DjoserUserViewSet.as_view({'get': 'me'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
