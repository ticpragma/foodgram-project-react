from django_filters import rest_framework as filters

from recipes.models import Ingredient, Tag, Recipe


class CustomFilterIngredient(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )


class CustomFlterRecipeTags(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    author = filters.NumberFilter(
        method='filter_author'
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def filter_is_favorited(self, queryset, u, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)

    def filter_is_in_shopping_cart(self, queryset, u, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(cart__user=user)

    def filter_author(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(author=value)
        else:
            return queryset
