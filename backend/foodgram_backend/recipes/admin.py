from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from django.contrib.admin import (
    ModelAdmin,
    TabularInline,
    display,
    register,
    site,
)
from django.utils.html import format_html
from recipes.forms import TagForm
from recipes.models import (
    IngredientInRecipe,
    Carts,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    Tag,
)

site.site_header = 'Администрирование Foodgram'

EMPTY_VALUE_DISPLAY = 'Значение не указано'


class IngredientInline(TabularInline):
    model = IngredientInRecipe
    extra = 2


class IngredientResource(resources.ModelResource):

    class Meta:
        model = Ingredient


@register(Ingredient)
class IngredientAdmin(ImportExportActionModelAdmin):
    resource_class = IngredientResource
    list_display = [
        field.name for field in Ingredient._meta.fields if field.name != 'id'
    ]


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'get_tags',
        'count_favorites'
    )
    fields = (
        (
            'name',
            'cooking_time',
        ),
        (
            'author',
            'tags',
        ),
        ('text',),
        ('image',),
    )
    raw_id_fields = ('author',)
    search_fields = (
        'name',
        'author__username',
        'tags__name',
    )
    list_filter = ('name', 'author__username', 'tags__name')

    inlines = (IngredientInline,)
    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY

    @display(description='Тэги')
    def get_tags(self, obj):
        list_ = [tag.name for tag in obj.tags.all()]
        return ', '.join(list_)

    @display(description='В избранном')
    def count_favorites(self, obj):
        return obj.in_favorites.count()


@register(Tag)
class TagAdmin(ModelAdmin):
    form = TagForm
    list_display = (
        'name',
        'slug',
        'color_code',
    )
    search_fields = ('name', 'color')

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY

    @display(description='Colored')
    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>', obj.color[1:], obj.color
        )


@register(FavoriteRecipe)
class FavoriteRecipesAdmin(ModelAdmin):
    list_display = ('user', 'recipes', 'date_added')
    search_fields = ('user__username', 'recipes__name')


@register(Carts)
class CardAdmin(ModelAdmin):
    list_display = ('user', 'recipes', 'date_added')
    search_fields = ('user__username', 'recipes__name')
