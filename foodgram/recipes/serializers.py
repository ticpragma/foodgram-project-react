from django.db.models import QuerySet, F
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.core.serializers import serialize
import json
from django.contrib.auth import get_user_model
from .models import Tag, Ingredient, Recipe, IngredientAmount, Favorite, ShoppingCart
from drf_extra_fields.fields import Base64ImageField



User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
    def get_id(self, obj):
        print(obj.id)
        return Recipe.objects.get(id=obj.id).id


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, ingredient):
        recipe = self.context.get('parent_model')
        ingredient_amount = ingredient.full_ingredient.all().get(recipe=recipe)
        return ingredient_amount.amount


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id')
    amount = serializers.IntegerField(min_value=1)
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()


    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_name(self, obj):
        return obj.ingredient.name
    
    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


def recipe_ingredients_set(recipe, ingredients) -> None:
    objs = []
    for i in ingredients:
        d = dict(i)
        objs.append(
            IngredientAmount(
                recipe=recipe, ingredient=Ingredient.objects.all().get(id=d['ingredient_id']), amount=d['amount']
            )
        )
    IngredientAmount.objects.bulk_create(objs)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = AddIngredientSerializer(many=True, source='full_ingredient')
    image = Base64ImageField()
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        tags: list[int] = validated_data.pop("tags")
        ingredients: dict[int, tuple] = validated_data.pop("full_ingredient")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe
    
    def update(self, recipe: Recipe, validated_data: dict):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("full_ingredient")

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe
    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if Favorite.objects.filter(user=user, recipe=obj).exists():
                return True
            return False
        return False
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if ShoppingCart.objects.filter(user=user, recipe=obj).exists():
                return True
            return False
        return False
    
    


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()
    author = AuthorSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        self.context['parent_model'] = instance
        return super().to_representation(instance)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if Favorite.objects.filter(user=user, recipe=obj).exists():
                return True
            return False
        return False
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if ShoppingCart.objects.filter(user=user, recipe=obj).exists():
                return True
            return False
        return False

