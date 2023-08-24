from django.contrib import admin
from recipes.models import *
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget

#class RecipesAdmin(admin.ModelAdmin):
#    """
#    Регистрация и настройка отображения модели Post в админке.
#    """
#    list_display = (
#        'pk',
#        'text',
#        'pub_date',
#        'author',
#        'tag',
#        'image',
#        'ingredients',
#    )
#    list_editable = ('ingredients','tag',)
#    search_fields = ('text',)
#    list_filter = ('pub_date',)
#    empty_value_display = '-пусто-'

#admin.site.register(Recipes, RecipesAdmin)
#admin.site.register(Tag)
#admin.site.register(RecipesIngredient)
#admin.site.register()
#admin.site.register(Ingredient)

class IngredientResource(resources.ModelResource):
    #category = fields.Field(
    #    category_name='category',
    #    attribute='category',
    #    widget=ForeignKeyWidget(IngredientCategory, 'name')
    #)

    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportActionModelAdmin):
    resource_class = IngredientResource
    list_display = [field.name for field in Ingredient._meta.fields if field.name != 'id']
    #inlines = [IngredientImageInline]

admin.site.register(Ingredient, IngredientAdmin)