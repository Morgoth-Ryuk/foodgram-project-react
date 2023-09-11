"""
Модуль вспомогательных функций.
"""
from datetime import datetime as dt
from typing import TYPE_CHECKING
# from urllib.parse import unquote

from django.apps import apps
from django.db.models import F, Sum
from foodgram_backend.settings import DATE_TIME_FORMAT
from recipes.models import IngredientInRecipe, Recipe

from recipes.models import Ingredient
from users.models import User


def create_shoping_list(user):
    """
    Сфомировать список ингридкетов для покупки.
    """
    today = date.today().strftime(DATE_TIME_FORMAT)
    shopping_list = [
        f'Список покупок {user.first_name}\n'
        f'{today}\n'
    ]

    ingredients = (
        Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values('name', measurement=F('measurement_unit'))
        .annotate(amount=Sum('recipe__amount'))
    )
    ing_list = (
        f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
        for ing in ingredients
    )
    shopping_list.extend(ing_list)

    filename = 'shopping_list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return '\n'.join(shopping_list)
