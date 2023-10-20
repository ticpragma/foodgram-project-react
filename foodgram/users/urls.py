from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet
urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
