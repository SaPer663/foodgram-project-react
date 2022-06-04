from django.contrib import admin

from recipes.models import (
    Ingredient, IngredientAmount, Recipe, RecipeTags, Tag,
)


class RecipeTagsInline(admin.TabularInline):
    """Тэги рецепта."""
    model = RecipeTags
    extra = 1


class IngredientAmountInline(admin.TabularInline):
    """Количество ингредиента."""
    model = IngredientAmount
    extra = 1


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Тэги."""
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('color',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    """Ингредиенты."""
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    """Рецепты."""
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    filter_horizontal = ('ingredients',)
    inlines = (RecipeTagsInline, IngredientAmountInline)
