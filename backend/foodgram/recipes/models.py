from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from pytils.translit import slugify

User = get_user_model()

TWENTY_LENGTH = 20
ONE_HUNDRED_LENGTH = 100
TWO_HUNDRED_LENGTH = 200


class Tag(models.Model):
    """Тэг рецептов."""
    name = models.CharField(
        'название',
        max_length=ONE_HUNDRED_LENGTH,
        unique=True
    )
    color = models.CharField('Цветовой HEX-код', max_length=7)
    slug = models.SlugField(
        'унифицированное имя тэга',
        max_length=TWO_HUNDRED_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    """Ингридиент рецепта."""
    name = models.CharField(
        'название',
        max_length=TWO_HUNDRED_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=TWO_HUNDRED_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='тэги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='ингредиенты'
    )
    name = models.CharField('название', max_length=TWO_HUNDRED_LENGTH)
    image = models.ImageField('изображение', upload_to='recipes/')
    text = models.TextField('описание')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=(MinValueValidator(1),)
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Количество ингредиента в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'количество',
        validators=(MinValueValidator(1),),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient'
            ),
        ]
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name}-{self.amount}'


class RecipeTags(models.Model):
    """Тэги рецептов."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='тэги рецептов'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        return f'{self.tag.name} - {self.recipe.name}'
