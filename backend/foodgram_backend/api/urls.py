# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from api.views import (UserViewSet, get_jwt_token, registration)
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    BaseAPIRootView,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    # СustomUserViewSet,
    # registration,
    # get_jwt_token
)

app_name = 'api'


class RuDefaultRouter(DefaultRouter):
    """
    Показывает описание главной страницы API на русском языке.
    """
    APIRootView = BaseAPIRootView


router = RuDefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = (
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/', include('djoser.urls.authtoken')),
)
