from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')


router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart/', RecipeViewSet, basename='recipes')

urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
