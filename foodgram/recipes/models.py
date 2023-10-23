from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Слаг',
        unique=True,
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name
        


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги'
    )
    image = models.ImageField(
        upload_to='recipes/media/images/',
        verbose_name='Картинка',
        help_text='Выберите картинку'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название'
    )
    text = models.CharField(
        max_length=1000,
        verbose_name='Текст',
        help_text='Сделайте описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(32000)),
        verbose_name='Время приготовления',
        help_text='Введите сколько готовить'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Укажите автора рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
        help_text='Укажите дату публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Название: {self.name}, автор: {self.author}'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='full_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='full_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(32000)),
        verbose_name='Количество'
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

    def __str__(self):
        return f'{self.recipe}: {self.ingredient}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name='Not unique favorite',
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.user}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name='Not unique ShoppingCart',
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.user}'
