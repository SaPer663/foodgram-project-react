from django.contrib.auth import get_user_model
from djoser.serializers import (
    TokenCreateSerializer, UserCreateSerializer,
    UserSerializer as DjoserUserSerializer,
)
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class CreateTokenSerializer(TokenCreateSerializer):
    """Сериалайзер для обработки данных при получении токена пользователя."""

    class Meta:
        model = User
        fields = ('password', 'email',)


class CreateUserSerializer(UserCreateSerializer):
    """Сериалайзер для обработки данных при создании пользователя."""

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'email', 'password',
            'first_name', 'last_name'
        )


class CustomUserSerializer(DjoserUserSerializer):
    """
    Сериалайзер модели пользователя.
    `is_subscribed: boolean` - Подписан ли текущий пользователь на этого
    пользователя.
    """
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id', 'username',
            'first_name', 'last_name',
            'password', 'is_subscribed'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.follower.filter(author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок пользователя."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )

    class Meta:
        model = Follow
        fields = (
            'email',
            'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'author', 'user'
        )
        read_only_fields = ('id',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('user')
        ret.pop('author')
        return ret

    def get_is_subscribed(self, obj):
        return obj.user.follower.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            return RecipeMinifiedSerializer(
                instance=obj.author.recipes.all()[:int(recipes_limit)],
                many=True
            ).data
        instance = obj.author.recipes.all()
        return RecipeMinifiedSerializer(
            instance=instance,
            many=True
        ).data

    def validate(self, data):
        author = self.initial_data.get('author')
        user = self.context.get('request').user
        if author == user:
            raise serializers.ValidationError(
                {'author': 'Нельзя подписаться на себя.'}
            )
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                {'author': 'Автор уже есть в ваших подписках.'}
            )
        return data


class UnfollowSerializer(serializers.ModelSerializer):
    """Сериализатор отписок пользователя от автора."""

    class Meta:
        model = Follow
        fields = ('user', 'author',)

    def validate(self, data):
        if not Follow.objects.filter(
            author=data.get('author'),
            user=data.get('user')
        ).exists():
            raise serializers.ValidationError(
                {'author': 'Автор не в подписках.'}
            )
        return data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Уменьшенный сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
