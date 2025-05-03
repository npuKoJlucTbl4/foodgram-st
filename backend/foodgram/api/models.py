from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.timezone import now


class SiteUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/',
                               blank=True,
                               null=True,
                               verbose_name='Аватар')
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Электронная почта')
    username = models.CharField(max_length=150,
                                blank=True,
                                null=True,
                                verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return str(self.username)


User = get_user_model()


class Recipe(models.Model):
    author = None
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
        plural_name = 'Рецепты'
        ordering = ['-date_published']

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
    recipe = None
    ingredient = None
    amount = models.IntegerField(validators=[MinValueValidator(1)],
                                 verbose_name="Количество")

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.amount} {self.ingredient} в {self.recipe.name}'
