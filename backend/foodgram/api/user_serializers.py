from django.contrib.auth import get_user_model
from djoser.serializers import (
    TokenCreateSerializer, UserCreateSerializer, UserSerializer,
)
from rest_framework.serializers import SerializerMethodField

User = get_user_model()


class CreateTokenSerializer(TokenCreateSerializer):
    """Сериалайзер для обработки данных при получении токена пользователя."""

    class Meta:
        model = User
        fields = ('password', 'email',)


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'email', 'password',
            'first_name', 'last_name'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserSerializer(UserSerializer):
    """
    Сериалайзер модели пользователя.
    `is_subscribed: boolean` - Подписан ли текущий пользователь на этого
    пользователя.
    """
    is_subscribed = SerializerMethodField()

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
