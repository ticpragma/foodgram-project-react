from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import TagViewSet, IngridientViewSet, RecipeViewSet


router = SimpleRouter()
router.register('ingredients', IngridientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
urlpatterns = [
    path('', include(router.urls))
]