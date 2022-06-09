from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'tags', views.TagsViewSet)
router.register(r'ingredients', views.IngredientsViewSet)
router.register(r'recipes', views.RecipesViewSet)
router.register(r'users', views.UsersViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Foodgram API",
        default_version='v1',
        description=("Сборник рецептов."),
    ),
    public=True,
)

urlpatterns = [
    path(
        'docs/',
        TemplateView.as_view(template_name='docs/redoc.html'),
        name='redoc'
    ),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'
    ),
    path(
        'swagger/', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
