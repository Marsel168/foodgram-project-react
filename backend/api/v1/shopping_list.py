from datetime import date

from django.db.models import F, Sum

from recipes.models import IngredientRecipe


def get_ingredients(user):
    shopping_list = (f'Список покупок для: {user}\n'
                     f'Дата: {date.today()}\n\n')
    len_str = 25
    shopping_list += '-' * len_str + '\n'
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_recipe__user=user
    ).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'amount', 'ingredient__measurement_unit'
    )
    for ingredient in ingredients:
        shopping_list += (
            f'{ingredient[0]}: {ingredient[1]} {ingredient[2]}\n'
        )
    shopping_list += '-' * len_str + '\n\n'
    shopping_list += 'Foodgram. Продуктовый помощник.'
    return shopping_list
