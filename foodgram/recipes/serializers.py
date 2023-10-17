from rest_framework import serializers
from .models import Tag, Ingridient, Recipe, RecipeAndIngredient
from drf_extra_fields.fields import Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    
class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    class Meta:
        model = Recipe
        fields = '__all__'