from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Follow

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка пользователя."""
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups', 'email', 'username'
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка подписки."""
    list_display = ('author', 'user')
    search_fields = (
        'author__username', 'author__email',
        'user__username', 'user__email',
    )
