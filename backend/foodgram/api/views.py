from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.serializers import (
    IngredientsSerializer, RecipesForReadingSerializer,
    RecipesForWritingSerializer, TagsSerializer,
)
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()
user = User.objects.get(username='saper663')


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()


class RecipesViewSet(ModelViewSet):

    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipesForReadingSerializer
        return RecipesForWritingSerializer
