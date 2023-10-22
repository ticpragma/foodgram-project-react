from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from users.models import Subscribe
from .models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientAmount
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeListSerializer, \
    FavoriteSerializer, SubscribeUserSerializer, SubscribeUserSerializerPres
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from core.filters import CustomFilterIngredient
from core.permissions import OwnerOrReadOnly

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
    permission_classes = (OwnerOrReadOnly,)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.filter(author=author)
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart', None)
        if is_in_shopping_cart is not None and is_in_shopping_cart == '1':
            queryset = queryset.filter(favorite__user_id=self.request.user.id)
        is_favorited = self.request.query_params.get('is_favorited', None)
        if is_favorited is not None and is_favorited == '1':
            queryset = queryset.filter(cart__user=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action in ('list',):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite(self, request, pk):
        if request.method == 'POST':
            if Recipe.objects.filter(pk=pk).exists():
                if not Favorite.objects.filter(user=request.user, recipe=get_object_or_404(Recipe, pk=pk)).exists():
                    Favorite.objects.create(user=request.user, recipe=get_object_or_404(Recipe, pk=pk))
                    recipe = Recipe.objects.get(id=pk)
                    serializer = FavoriteSerializer(recipe)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if Favorite.objects.filter(user=request.user, recipe=get_object_or_404(Recipe, pk=pk)).exists():
                Favorite.objects.filter(user=request.user, recipe=get_object_or_404(Recipe, pk=pk)).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            if Recipe.objects.filter(pk=pk).exists():
                recipe = get_object_or_404(Recipe, pk=pk)
                if not ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                    ShoppingCart.objects.create(user=request.user, recipe=recipe)
                    serializer = FavoriteSerializer(recipe)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=request.user, recipe=get_object_or_404(Recipe, pk=pk)).exists():
                ShoppingCart.objects.filter(user=request.user, recipe=get_object_or_404(Recipe, pk=pk)).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class DownloadShoppingCartAPIView(APIView):
    def get(self, request):
        ingredient_dict = {}
        cart = (ShoppingCart.objects.filter(user=request.user))
        for i in cart:
            recipe = Recipe.objects.get(id=i.recipe.id)
            ingr_amount = IngredientAmount.objects.filter(recipe=recipe)
            for ingr_am in ingr_amount:
                ingredients = Ingredient.objects.get(id=ingr_am.ingredient.id)
                ingredient_dict[(ingredients.name, ingredients.measurement_unit)] = ingredient_dict.get(
                    (ingredients.name, ingredients.measurement_unit), 0) + ingr_am.amount
        content = 'Список ингредиентов:'
        for (name, unit), amount in ingredient_dict.items():
            content = content + '\n' + name + ' ' + str(amount) + ' ' + unit
        print(content)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment'
        return response


class SubAPIView(APIView):
    def post(self, request, pk):
        if request.user and request.user.is_authenticated:
            user = request.user
            to_user = get_object_or_404(User, pk=pk)
            if user != to_user and not Subscribe.objects.filter(user=user, author=to_user).exists():
                Subscribe.objects.create(user=user, author=to_user)
                limit = request.query_params.get('recipes_limit', None)
                context = {}
                if limit:
                    context['limit'] = int(limit)
                serializer = SubscribeUserSerializerPres(to_user, context=context)
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user and request.user.is_authenticated:
            user = request.user
            to_user = get_object_or_404(User, pk=pk)
            if user != to_user and Subscribe.objects.filter(user=user, author=to_user).exists():
                Subscribe.objects.get(user=user, author=to_user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SubViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeUserSerializer

    def get_queryset(self):
        user = self.request.user
        limit = self.request.query_params.get('recipes_limit', None)
        queryset = Subscribe.objects.filter(user=user)
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
