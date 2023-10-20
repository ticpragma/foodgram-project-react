from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import TagViewSet, IngredientViewSet, RecipeViewSet, DownloadShoppingCartAPIView


router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShoppingCartAPIView.as_view()),
    path('', include(router.urls))
]