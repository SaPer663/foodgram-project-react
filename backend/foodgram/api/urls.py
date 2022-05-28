from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'tags', views.TagsViewSet)
router.register(r'ingredients', views.IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
