from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator
from rest_framework.exceptions import ValidationError

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
    )
    color = models.CharField(
        max_length=7,
        blank=False
    )
    slug = models.SlugField(
        max_length=200,
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$'
            )
        ]
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False
    )


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/media/images/'
    )
    name = models.CharField(
        max_length=200
    )
    text = models.CharField(max_length=1000)
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),)
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes'
    )


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='full_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='full_ingredient'
    )
    amount = models.IntegerField(
        blank=False
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredient",
                ),
                name='Not unique ingredient',
            ),
        )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
