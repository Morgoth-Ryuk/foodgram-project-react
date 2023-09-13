from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    author = filters.AllValuesFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        field_name='favorites',
        method='_choice_filter',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppingcart',
        method='_choice_filter',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _choice_filter(self, queryset, key, value):
        if value:
            return queryset.filter(**{f'{key}__user': self.request.user})
        return queryset
