from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class SiteUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/',
                               blank=True,
                               null=True,
                               verbose_name='Аватар')
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Электронная почта')
    username = models.CharField(max_length=150,
                                validators=[RegexValidator(
                                    r'^[a-zA-Z0-9_.-]+$')],
                                verbose_name='Имя пользователя',
                                unique=True)
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


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Пользователь')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_user_author')]
        ordering = ['id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
