from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from .models import (Tag,
                     Ingredient,
                     Recipe,
                     IngredientAmount)
from core.consts import MAX_COOK_AMOUNT_TIME, MIN_COOK_AMOUNT_TIME


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
    amount = serializers.IntegerField(
        min_value=MIN_COOK_AMOUNT_TIME,
        max_value=MAX_COOK_AMOUNT_TIME
    )
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.current_user.all().filter(author=obj).exists())


def ingredient_amount_create(recipe, ingredients):
    objs = []
    for ingredient in ingredients:
        objs.append(
            IngredientAmount(
                recipe=recipe,
                ingredient=Ingredient.objects.all().get(
                    id=ingredient['ingredient_id']),
                amount=ingredient['amount']
            )
        )
    IngredientAmount.objects.bulk_create(objs)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, write_only=True)
    ingredients = AddIngredientSerializer(many=True, source='full_ingredient')
    image = Base64ImageField()
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        max_value=MAX_COOK_AMOUNT_TIME,
        min_value=MIN_COOK_AMOUNT_TIME
    )

    class Meta:
        model = Recipe
        fields = ('id',
                  'ingredients',
                  'image',
                  'author',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'cooking_time',
                  'name',
                  'text',
                  'tags')

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ingredients не должно быть пустым')
        unique = set()
        for ingredient in ingredients:
            id = ingredient['ingredient_id']
            if not Ingredient.objects.filter(id=id).exists():
                raise serializers.ValidationError(
                    'Все ингредиенты должны существовать')
            unique.add(id)
        if len(unique) != len(ingredients):
            raise serializers.ValidationError(
                'Не должно быть повторяющихся ингредиентов')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Поле tags не должно быть пустым')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Не должно быть повторяющихся тэгов')
        return tags

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Поле image не должно быть пустым')
        return image

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('full_ingredient')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_amount_create(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('full_ingredient', None)
        if not tags:
            raise serializers.ValidationError('Должно быть поле tags')
        if not ingredients:
            raise serializers.ValidationError('Должно быть поле ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            ingredient_amount_create(recipe, ingredients)

        recipe.save()
        return recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.favorite.all().filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.cart.all().filter(recipe=obj).exists())

    def to_representation(self, instance):
        serialized = TagSerializer(instance.tags, many=True)
        data = super().to_representation(instance)
        data['tags'] = serialized.data
        return data


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
        return (user.is_authenticated
                and user.favorite.all().filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.cart.all().filter(recipe=obj).exists())


class ShortReciperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeUserSerializer(serializers.ModelSerializer):
    recipes = ShortReciperSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'limit' in self.context:
            if self.context['limit'] < len(data['recipes']):
                data['recipes'] = data['recipes'][:self.context['limit']]
        return data

    def get_recipes_count(self, obj):
        recipes_count = obj.recipes.count()
        return min(self.context.get('limit', recipes_count), recipes_count)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.current_user.all().filter(author=obj).exists())


class SubscribeUserSerializerPres(serializers.ModelSerializer):
    recipes = ShortReciperSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'limit' in self.context:
            if self.context['limit'] < len(data['recipes']):
                data['recipes'] = data['recipes'][:self.context['limit']]
        return data

    def get_recipes_count(self, obj):
        recipes_count = obj.recipes.count()
        return min(self.context.get('limit', recipes_count), recipes_count)

    def get_is_subscribed(self, obj):
        user = User.objects.get(id=obj.id)
        return user.is_authenticated
