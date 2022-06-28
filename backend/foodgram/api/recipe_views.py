from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import AuthorAndTagFilter
from api.recipe_serializers import (
    FavoritesSerializer, IngredientsSerializer, RecipesForReadingSerializer,
    RecipesForWritingSerializer, ShoppingCartSerializer, TagsSerializer,
)
from api.utilits import LimitPagePagination, get_shopping_cart_pdf
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from users.permissions import AuthorOrReadOnly

CONTENT_TYPE = 'application/pdf'
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
    search_fields = ('name',)


class RecipesViewSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = LimitPagePagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AuthorAndTagFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipesForReadingSerializer
        return RecipesForWritingSerializer

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """
        Добавление рецепта в список избранных рецептов.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoritesSerializer(data={
            'recipe': recipe.id,
            'user': request.user.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data, status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        """
        Удаление рецепта из списока избранных рецептов.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            instance = Favorites.objects.get(
                recipe=recipe,
                user=request.user
            )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                data={'errors': 'Рецепта нет в избранных'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=('post',),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """
        Добавление(удаление) ингредиентов рецепта в(из) список(ка) покупок.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartSerializer(
            data={'recipe': recipe.id, 'user': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def del_from_shopping_cart(self, request, pk):
        """
        Удаление ингредиентов рецепта из списока покупок.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            ShoppingCart.objects.get(
                recipe=recipe, user=request.user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                data={'errors': 'Рецепта нет в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        shopping_cart_queryset = request.user.shopping_carts.values(
            name=F('recipe__ingredient_amounts__ingredient__name'),
            unit=F('recipe__ingredient_amounts__ingredient__measurement_unit')
        ).annotate(amount=Sum('recipe__ingredient_amounts__amount'))
        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename={settings.UPLOAD_FILE_NAME}'
        )
        return get_shopping_cart_pdf(shopping_cart_queryset, response)
