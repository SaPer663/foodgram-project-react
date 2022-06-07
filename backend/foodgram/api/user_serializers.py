from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class CreateTokenSerializer(serializers.ModelSerializer):
    """Сериалайзер для обработки данных при получении токена пользователя."""

    class Meta:
        model = User
        fields = ('password', 'email',)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериалайзер модели пользователя.
    `is_subscribed: boolean` - Подписан ли текущий пользователь на этого
    пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

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
