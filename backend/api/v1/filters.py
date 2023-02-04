from django_filters.rest_framework import (FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Tag


class RecipeFilter(FilterSet):
    is_favorited = NumberFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    author = NumberFilter(
        field_name='author__id',
    )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_recipe__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)
