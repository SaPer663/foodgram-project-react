from django.contrib.auth import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Изменены свойства поля `email`, т.е. добавлено значение уникальности и
    поле обязательно для заполнения.
    """
    email = models.EmailField(
        'электронная почта',
        unique=True
    )

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Follow(models.Model):
    """Подписка."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following', verbose_name='автор'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower', verbose_name='подписчик'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        )

    def __str__(self):
        return f'{self.author.username} - {self.user.username}'
