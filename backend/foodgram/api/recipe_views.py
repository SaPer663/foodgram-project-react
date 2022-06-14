from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import AuthorAndTagFilter
from api.recipe_serializers import (
    FavoritesSerializer, IngredientsSerializer, RecipesForReadingSerializer,
    RecipesForWritingSerializer, TagsSerializer,
)
from core.pagination import LimitPagePagination
from recipes.models import Favorites, Ingredient, Recipe, Tag
from users.permissions import AuthorOrReadOnly

User = get_user_model()


class TagsViewSet(ReadOnlyModelViewSet):
    """Представление тэгов рецептов."""
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Представление иногредиентов рецептов."""
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = LimitPagePagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = AuthorAndTagFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipesForReadingSerializer
        return RecipesForWritingSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            try:
                instance = Favorites.objects.get(
                    recipe=recipe,
                    user=request.user
                )
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = FavoritesSerializer(data={
            'recipe': pk,
            'user': request.user.id
        })
        serializer.is_valid(raise_exception=True)
        Favorites.objects.create(recipe=recipe, user=request.user)
        data = serializer.data.copy()
        data.pop('recipe')
        data.pop('user')
        return Response(data=data, status=status.HTTP_201_CREATED)
