from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.recipes_serializers import (
    IngredientsSerializer, RecipesForReadingSerializer,
    RecipesForWritingSerializer, TagsSerializer,
)
from api.user_serializers import UserSerializer
from core.pagination import LimitPagePagination
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class UsersViewSet(UserViewSet):
    """Представление списка пользователей."""
    serializer_class = UserSerializer
    pagination_class = LimitPagePagination


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()


class RecipesViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    pagination_class = LimitPagePagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipesForReadingSerializer
        return RecipesForWritingSerializer
