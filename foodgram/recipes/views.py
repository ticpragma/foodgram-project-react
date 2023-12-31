from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from core.filters import CustomFilterIngredient, CustomFlterRecipeTags
from core.permissions import OwnerOrReadOnly
from users.models import Subscribe
from .models import (Tag,
                     Ingredient,
                     Recipe,
                     Favorite,
                     ShoppingCart)
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          RecipeListSerializer,
                          FavoriteSerializer,
                          SubscribeUserSerializer,
                          SubscribeUserSerializerPres)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    search_fields = ('name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilterIngredient
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (OwnerOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CustomFlterRecipeTags

    def get_serializer_class(self):
        if self.action in ('list',):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self._create_obj(
                Favorite,
                request.user,
                recipe,
                request.user.favorite.all().filter(recipe=recipe))
        if request.method == 'DELETE':
            favorite = request.user.favorite.all().filter(recipe=recipe)
            return self._delete_obj(favorite)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self._create_obj(
                ShoppingCart,
                request.user,
                recipe,
                request.user.cart.all().filter(recipe=recipe))
        if request.method == 'DELETE':
            shopping_cart = request.user.cart.all().filter(recipe=recipe)
            return self._delete_obj(shopping_cart)

    @staticmethod
    def _create_obj(cls, user, recipe, queryset):
        if not queryset.exists():
            cls.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _delete_obj(obj):
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DownloadShoppingCartAPIView(APIView):
    def get(self, request):
        ingredient_dict = {}
        cart = request.user.cart.all()
        for product in cart:
            recipe = Recipe.objects.get(id=product.recipe.id)
            ingredient_amount = recipe.full_ingredient.all()
            self._group_amounts_by_ingredient(
                ingredient_amount,
                ingredient_dict)
        content = 'Список ингредиентов:'
        for (name, unit), amount in ingredient_dict.items():
            content = content + f'\n{name} {amount} {unit}'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment'
        return response

    @staticmethod
    def _group_amounts_by_ingredient(ingr_amount, ingredient_dict):
        for ingredient_amount in ingr_amount:
            ingredient = Ingredient.objects.get(
                id=ingredient_amount.ingredient.id)
            key = (ingredient.name, ingredient.measurement_unit)
            ingredient_dict[key] = (
                ingredient_dict.get(key, 0) + ingredient_amount.amount)


class SubAPIView(APIView):
    def post(self, request, pk):
        if request.user and request.user.is_authenticated:
            user = request.user
            to_user = get_object_or_404(User, pk=pk)
            if (user != to_user
                and not user.current_user.all().filter(
                    author=to_user).exists()):
                Subscribe.objects.create(user=user, author=to_user)
                limit = request.query_params.get('recipes_limit', None)
                context = {}
                if limit:
                    context['limit'] = int(limit)
                serializer = SubscribeUserSerializerPres(to_user,
                                                         context=context)
                return Response(status=status.HTTP_201_CREATED,
                                data=serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user and request.user.is_authenticated:
            user = request.user
            to_user = get_object_or_404(User, pk=pk)
            subs = user.current_user.all().filter(author=to_user)
            if user != to_user and subs.exists():
                subs.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SubViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeUserSerializer

    def get_queryset(self):
        user = self.request.user
        limit = self.request.query_params.get('recipes_limit', None)
        queryset = user.current_user.all()
        if limit:
            self.limit = int(limit)
        res = []
        for sub_user in queryset:
            res.append(sub_user.author)
        return res

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self, 'limit'):
            context['limit'] = self.limit
        return context
