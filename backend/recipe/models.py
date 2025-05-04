from django.db import models
from django.core.validators import MinValueValidator
from django.utils.timezone import now

from user.models import User


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="recipes", verbose_name='Автор')
    name = models.CharField(max_length=128, verbose_name="Название")
    image = models.ImageField(verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)')
    date_published = models.DateTimeField(
        default=now,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-date_published']

    def get_absolute_url(self):
        return f'/recipes/{self.pk}'

    def __str__(self):
        return str(self.name)


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название")
    measurment_unit = models.CharField(
        max_length=30,
        verbose_name="Ед. измерения")

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="recipe_ingredients",
                               verbose_name="Рецепт")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name="recipe_ingredients",
                                   verbose_name="Ингредиенты")
    amount = models.IntegerField(validators=[MinValueValidator(1)],
                                 verbose_name="Количество")

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.amount} {self.ingredient} в {self.recipe.name}'


class BaseUserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Favorite(BaseUserRecipeRelation):
    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(BaseUserRecipeRelation):
    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
