from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe

User = get_user_model()


class AuthorAndTagFilter(FilterSet):
    """
    Фильтр рецептов по тэгам и автору.
    Фильтрация по тэгу происходит по `slug`;
    `is_favorited` фильтрует по рецептам, которые находятся в списке избранных;
    `is_in_shopping_cart` фильтрует по рецептам, ингредиенты которых добавленны
    в список покупок.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
