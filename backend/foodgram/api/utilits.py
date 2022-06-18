import os

import reportlab.rl_config

from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.pagination import PageNumberPagination

reportlab.rl_config.TTFSearchPath.append(
    str(os.path.join(settings.STATIC_ROOT, 'ttfonts'))
)


class LimitPagePagination(PageNumberPagination):
    """Страничный паджинатор.
    `limit` - задаёт количество объектов на странице.
    """
    page_size = 6
    page_size_query_param = 'limit'


def get_shopping_cart_pdf(request, shopping_cart_queryset, response):
    """
    Создаёт PDF файл с данными перданного queryset.
    Каждый объект queryset имеет ключи: `name`, `amount`, `unit`.
    """
    pdfmetrics.registerFont(
        TTFont('Arial', 'arial.ttf', 'UTF-8')
    )
    page = canvas.Canvas(response)
    page.setFont('Arial', size=24)
    page.drawString(200, 800, 'Список ингредиентов')
    page.setFont('Arial', size=16)
    height = 750
    for i, item in enumerate(shopping_cart_queryset, 1):
        page.drawString(
            75,
            height,
            (
                f"{i}.  {item['name']} - {item['amount']} {item['unit']}"
            ),
        )
        height -= 25
    page.showPage()
    page.save()
    return response
