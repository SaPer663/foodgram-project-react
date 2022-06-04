import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (
    Ingredient, IngredientAmount, Recipe, RecipeTags, Tag,
)


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


class IngredientAmountForReadingSerializer(serializers.ModelSerializer):
    """Сериалайзер количества ингредиента для дествий `retrieve, list`."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientAmountForWritingSerializer(serializers.ModelSerializer):
    """Сериалайзер количества ингредиента для дествий `create, update`."""

    id = serializers.IntegerField(source='ingredient.id',)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериалайзер тэга."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipesForReadingSerializer(serializers.ModelSerializer):
    """Сериалайзер рецепта для действий `retrieve, list`."""
    ingredients = IngredientAmountForReadingSerializer(
        many=True,
        read_only=True,
        source='ingredient_amounts'
    )
    image = Base64ImageField()
    tags = TagsSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags', 'ingredients',
            'name', 'text',
            'image', 'cooking_time'
        )


class RecipesForWritingSerializer(serializers.ModelSerializer):
    """Сериалайзер рецепта для дествий `create, update`."""
    ingredients = IngredientAmountForWritingSerializer(
        many=True,
        source='ingredient_amounts'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags', 'ingredients',
            'name', 'text',
            'image', 'cooking_time'
        )

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
                    'Проверьте, что ингредиенты не павторяются'
                )
            ingredient_set.add(ingredient_id)
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        for tag in set(tags):
            RecipeTags.objects.create(recipe=recipe, tag=tag)
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
        return recipe
