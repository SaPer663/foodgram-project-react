from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

TWENTY_LENGTH = 20
ONE_HUNDRED_LENGTH = 100


class Tag(models.Model):
    """Тэг рецептов."""
    name = models.CharField('название', max_length=ONE_HUNDRED_LENGTH)
    color = models.CharField('Цветовой HEX-код', max_length=TWENTY_LENGTH)
    slug = models.SlugField('унифицированное имя тэга', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиент рецепта."""
    name = models.CharField(
        'название',
        max_length=ONE_HUNDRED_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=ONE_HUNDRED_LENGTH
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
        verbose_name='тэги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientQuantity',
        verbose_name='ингредиенты'
    )
    is_favorited = models.BooleanField('в избранном', default=False)
    is_in_shopping_cart = models.BooleanField(
        'в списке покупок',
        default=False
    )
    name = models.CharField('название', max_length=ONE_HUNDRED_LENGTH)
    image = models.ImageField('изображение', upload_to='recipes/')
    text = models.TextField('описание')
    cooking_time = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredientQuantity(models.Model):
    """Количество ингредиента в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.title}-{self.amount}'


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
