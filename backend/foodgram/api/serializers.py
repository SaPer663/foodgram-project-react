from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'
