from django.contrib import admin
from django.urls import path, include
from recipes.views import SubViewSet
from rest_framework.routers import SimpleRouter

urlpatterns = [
    path('api/users/subscriptions/', SubViewSet.as_view({'get': 'list'})),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls'))
]
