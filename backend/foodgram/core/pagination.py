from rest_framework.pagination import PageNumberPagination


class LimitPagePagination(PageNumberPagination):
    """Страничный паджинатор.
    `limit` - задаёт количество объектов на странице.
    """
    page_size = 5
    page_size_query_param = 'limit'
