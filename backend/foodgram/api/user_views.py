from django.contrib.auth import get_user_model
# from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

# from api.filters import AuthorAndTagFilter
# from api.recipe_serializers import (
#     FavoritesSerializer, IngredientsSerializer, RecipesForReadingSerializer,
#     RecipesForWritingSerializer, TagsSerializer,
# )
from api.user_serializers import CustomUserSerializer, UsersFollowingSerializer
from core.pagination import LimitPagePagination
# from recipes.models import Recipe
from users.models import Follow

# from users.permissions import AuthorOrReadOnly

User = get_user_model()


class UsersViewSet(DjoserUserViewSet):
    """Представление данных пользователей."""
    serializer_class = CustomUserSerializer
    pagination_class = LimitPagePagination

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        pagination_class=LimitPagePagination
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        if pages is None:
            serializer = UsersFollowingSerializer(
                instance=queryset, many=True, context={'request': request}
            )
            return Response(serializer.data)
        serializer = UsersFollowingSerializer(
            instance=pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        is_subscription = Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
        if request.method == 'DELETE':
            if not is_subscription:
                raise ValidationError({'author': 'Автор не в подписках.'})
            Follow.objects.get(author=author, user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if is_subscription:
            raise ValidationError(
                {'author': 'Автор уже есть в ваших подписках.'}
            )
        if author == request.user:
            raise ValidationError({'author': 'Нельзя подписаться на себя.'})
        instance = Follow.objects.create(author=author, user=request.user)
        serializer = UsersFollowingSerializer(
            instance=instance,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
