from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from api.user_serializers import CustomUserSerializer, RecipeMinifiedSerializer
from recipes.models import (
    Favorites, Ingredient, IngredientAmount, Recipe, RecipeTags, ShoppingCart,
    Tag,
)

User = get_user_model()


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериалайзер количества ингредиента."""

    id = serializers.IntegerField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериалайзер тега."""

    name = serializers.CharField(
        max_length=200,
        validators=(
            UniqueValidator(
                queryset=Tag.objects.all(),
                message='Тег с таким именем уже есть'
            ),
        )
    )
    slug = serializers.SlugField(
        max_length=200,
        validators=(
            UniqueValidator(
                queryset=Tag.objects.all(),
                message='Тег с таким слагом уже есть'
            ),
        )
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class RecipesForReadingSerializer(serializers.ModelSerializer):
    """
    Сериалайзер рецепта для действий `retrieve, list`.
    `is_favorited: boolean` - находится ли рецепт в списке избранных рецептов
    текущего пользователя, если пользователь не зарегистрирован - выведет
    False;
    `is_in_shopping_cart: boolean` - находится ли ингредиенты рецепта в списке
    для покупок.
    """

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        read_only=True,
        source='ingredient_amounts'
    )
    image = Base64ImageField()
    tags = TagsSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name', 'text',
            'image', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Находится ли рецепт в списке избранном текущего пользователя."""
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Находиться ли рецепт в списке покупок текущего пользователя."""
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.shopping_carts.filter(recipe=obj).exists()


class RecipesForWritingSerializer(serializers.ModelSerializer):
    """Сериалайзер рецепта для дествий `create, update`."""
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredient_amounts'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags', 'ingredients',
            'name', 'text',
            'image', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Находится ли рецепт в списке избранном текущего пользователя."""
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Находиться ли рецепт в списке покупок текущего пользователя."""
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.shopping_carts.filter(recipe=obj).exists()

    def validate(self, data):
        ingredients = data.get('ingredient_amounts')
        if ingredients is None:
            raise serializers.ValidationError(
                'Необходимо указать хоть один ингредиент'
            )
        ingredient_set = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in ingredient_set:
                raise serializers.ValidationError(
                    'Проверьте, что ингредиенты не повторяются'
                )
            ingredient_set.add(ingredient_id)
        return data

    def _write_tags(self, recipe, tags):
        recipe_tags = (
            RecipeTags(recipe=recipe, tag=tag) for tag in set(tags))
        RecipeTags.objects.bulk_create(recipe_tags)

    def _write_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient.get('ingredient').get('id')
            )
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        self._write_tags(recipe, tags)
        self._write_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')
        recipe = super().update(recipe, validated_data)
        recipe.tags.clear()
        recipe.ingredients.clear()
        self._write_tags(recipe, tags)
        self._write_ingredients(recipe, ingredients)
        return recipe


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список избранных рецептов."""

    class Meta:
        model = Favorites
        fields = ('recipe', 'user')
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True}
        }
        validators = (
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=('user', 'recipe'),
            ),
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(RecipeMinifiedSerializer(
            instance=self.validated_data.get('recipe')
        ).data)
        return ret


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов рецепта в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True}
        }
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
            ),
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(RecipeMinifiedSerializer(
            instance=self.validated_data.get('recipe')
        ).data)
        return ret
