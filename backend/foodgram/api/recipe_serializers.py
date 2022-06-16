import base64
import imghdr
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.user_serializers import CustomUserSerializer
from recipes.models import (
    Favorites, Ingredient, IngredientAmount, Recipe, RecipeTags, Tag,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Поле картинки, закодированной в base64."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                'Incorrect type. Expected a string, but got '
                f'{type(data).__name__}'
            )
        if 'data:' in data and ';base64,' in data:
            _, data = data.split(';base64,')
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            raise serializers.ValidationError('Invalid image')

        file_name = str(uuid.uuid4())[:12]
        file_extension = self.get_file_extension(file_name, decoded_file)
        complete_file_name = f'{file_name}.{file_extension}'
        data = ContentFile(decoded_file, name=complete_file_name)

        return super().to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        return 'jpg' if extension == 'jpeg' else extension


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиента."""

    class Meta:
        model = Ingredient
        fields = '__all__'


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
    """Сериалайзер тэга."""

    class Meta:
        model = Tag
        fields = '__all__'


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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать хоть один ингредиент'
            )
        ingredient_set = set()
        for ingredient in value:
            ingredient_id = ingredient.get('ingredient').get('id')
            if ingredient_id in ingredient_set:
                raise serializers.ValidationError(
                    'Проверьте, что ингредиенты не повторяются'
                )
            ingredient_set.add(ingredient_id)
        return value

    def validate_name(self, value):
        current_user = self.context.get('request').user
        if Recipe.objects.filter(author=current_user, name=value).exists():
            raise serializers.ValidationError(
                'Рецепт с таким именем у вас уже есть.'
            )
        return value

    def _write_tags(self, recipe, tags):
        for tag in set(tags):
            RecipeTags.objects.create(recipe=recipe, tag=tag)

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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        self._write_tags(recipe, tags)
        self._write_ingredients(recipe, ingredients)
        return recipe

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
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorites
        fields = ('id', 'name', 'image', 'cooking_time', 'recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=('user', 'recipe'),
            )
        ]
