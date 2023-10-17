from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model


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

class Ingridient(models.Model):
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
        Ingridient,
        related_name='recipes',
        through='RecipeAndIngredient'
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
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes'
    )

class RecipeAndIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='full_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name='full_ingredient'
    )
    amount = models.IntegerField(
        blank=False
    )
