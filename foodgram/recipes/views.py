from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientAmount
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeListSerializer, FavoriteSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list',):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def favorite(self, request, pk):
        if request.method == 'POST':
            Favorite.objects.create(user=request.user, recipe=Recipe.objects.get(id=pk))
            recipe = Recipe.objects.get(id=pk)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if Favorite.objects.filter(user=request.user, recipe=Recipe.objects.get(id=pk)).exists():
                Favorite.objects.filter(user=request.user, recipe=Recipe.objects.get(id=pk)).delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            ShoppingCart.objects.create(user=request.user, recipe=Recipe.objects.get(id=pk))
            recipe = Recipe.objects.get(id=pk)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=request.user, recipe=Recipe.objects.get(id=pk)).exists():
                ShoppingCart.objects.filter(user=request.user, recipe=Recipe.objects.get(id=pk)).delete()
                return Response(status=status.HTTP_200_OK)
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
                ingredient_dict[(ingredients.name, ingredients.measurement_unit)] = ingredient_dict.get((ingredients.name, ingredients.measurement_unit), 0) + ingr_am.amount
        content = 'Список ингредиентов:'
        for (name, unit), amount in ingredient_dict.items():
            content = content + '\n' + name + ' ' + str(amount) + ' ' + unit
        print(content)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment'
        return response
        
