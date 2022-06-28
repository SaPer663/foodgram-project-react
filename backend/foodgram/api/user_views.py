from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.user_serializers import (
    CustomUserSerializer, FollowSerializer, UnfollowSerializer,
)
from api.utilits import LimitPagePagination
from users.models import Follow

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
        """
        Возвращает пользователей, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        """
        queryset = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        if pages is None:
            serializer = FollowSerializer(
                instance=queryset, many=True, context={'request': request}
            )
            return Response(serializer.data)
        serializer = FollowSerializer(
            instance=pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post',),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Подписаться на пользователя."""
        author = get_object_or_404(User, id=id)
        serializer = FollowSerializer(
            data={'author': author.id, 'user': request.user.id},
            context={
                'request': request,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        serializer = UnfollowSerializer(
            data={'author': author.id, 'user': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.get(author=author, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
