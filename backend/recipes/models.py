from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from foodgram.settings import AUTH_USER_MODEL


class Recipe(models.Model):
    """ Модель рецептов. """

    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=128,
        unique=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги',
        related_name='recipes'
    )
    text = models.TextField('Текстовое описание', blank=True, null=True)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(1, message='Укажите время больше нуля!'),
        )
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """ Модель тэгов. """

    name = models.CharField('Название тэга', max_length=128, unique=True)
    color = ColorField(default='#FF0000')
    slug = models.SlugField('Адрес', unique=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=32,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель ингредиентов в рецептах."""

    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Название ингредиента',
        related_name='ingredient_recipe'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество больше нуля!',
        ),),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient}'


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_favorite'
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_user'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_recipe'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} у пользователя {self.user}'
