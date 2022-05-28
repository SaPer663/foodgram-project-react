from rest_framework.viewsets import ReadOnlyModelViewSet

from api.serializers import IngredientsSerializer, TagsSerializer
from recipes.models import Ingredient, Tag


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
