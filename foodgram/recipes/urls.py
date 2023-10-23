from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (TagViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    DownloadShoppingCartAPIView,
                    SubAPIView,
                    SubViewSet)


router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
urlpatterns = [
    path('users/subscriptions/',
         SubViewSet.as_view({'get': 'list'})),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartAPIView.as_view()),
    path('users/<int:pk>/subscribe/',
         SubAPIView.as_view()),
    path('', include(router.urls))
]
