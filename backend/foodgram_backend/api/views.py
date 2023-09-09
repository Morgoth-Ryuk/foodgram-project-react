# from django.shortcuts import get_object_or_404
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
# from rest_framework import permissions, status, viewsets
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend
# from foodgram_backend.settings import FROM_EMAIL
###############

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from django.db.models import Q, QuerySet
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet

from users.models import User, Subscription
from recipes.models import Carts, FavoriteRecipe, Ingredient, Recipe, Tag
from api.mixins import AddDelViewMixin
from api.paginators import PageLimitPagination
from api.permissions import (
    AdminOrReadOnly,
    AuthorStaffOrReadOnly,
    IsAuthenticated,
)
from api.serializers import (
    IngredientSerializer,
    RecipesCreateSerializer,
    TagSerializer,
    UserSubscribeSerializer,
    RecipeReadSerializer,
)
from core.const import Tuples, UrlQueries
from core.services import create_shoping_list


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """
    Работает с пользователями.

    ViewSet для работы с пользователми - вывод таковых,
    регистрация.
    Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """
    serializer_class = UserSubscribeSerializer
    http_method_names = ('get', 'post', 'delete')
    queryset = User.objects.all()

    pagination_class = PageLimitPagination
    permission_classes = (AllowAny,)
    link_model = Subscription

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """
        Создаёт/удалет связь между пользователями.
        """

    @subscribe.mapping.post
    def create_subscribe(self, request, id):
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        return self._delete_relation(Q(author__id=id))

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """
        Список подписок пользоваетеля.
        """
        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """
    Работает с тэгами.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Работет с игридиентами.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):
        """
        Получение queryset в соответствии с параметрами запроса.
        """
        name = self.request.query_params.get(UrlQueries.SEARCH_ING_NAME)
        queryset = self.queryset

        if not name:
            return queryset

        start_queryset = queryset.filter(name__istartswith=name)
        start_names = (ing.name for ing in start_queryset)
        contain_queryset = queryset.filter(name__icontains=name).exclude(
            name__in=start_names
        )
        return list(start_queryset) + list(contain_queryset)


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """
    Работает с рецептами.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipesCreateSerializer
    permission_classes = [AuthorStaffOrReadOnly]
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipesCreateSerializer
    
    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        """
        Формирует файл *.txt со списком покупок.
        """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = create_shoping_list(user)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
