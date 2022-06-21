from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import AuthorAndTagFilter
from api.recipe_serializers import (
    FavoritesSerializer, IngredientsSerializer, RecipesForReadingSerializer,
    RecipesForWritingSerializer, TagsSerializer,
)
from api.user_serializers import RecipeMinified
from api.utilits import LimitPagePagination, get_shopping_cart_pdf
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
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
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """
        Добавление(удаление) рецептов в(из) список(ка) избранных рецептов.
        """
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

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """
        Добавление(удаление) ингредиентов рецепта в(из) список(ка) покупок
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe, user=request.user
        ).exists()
        if request.method == 'DELETE':
            if not in_shopping_cart:
                raise ValidationError(
                    {'recipe': 'Рецепта нет в списке покупок.'}
                )
            ShoppingCart.objects.get(
                recipe=recipe, user=request.user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if in_shopping_cart:
            raise ValidationError(
                {'recipe': 'Рецепт уже в списке покупок.'}
            )
        ShoppingCart.objects.create(
            recipe=recipe, user=request.user
        )
        return Response(
            RecipeMinified(instance=recipe).data,
            status=status.HTTP_201_CREATED
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
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; ' 'filename="shopping_cart.pdf"'
        )
        return get_shopping_cart_pdf(shopping_cart_queryset, response)
