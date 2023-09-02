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
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, QuerySet
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet

from users.models import User, Subscriptions
from recipes.models import Carts, FavoriteRecipes, Ingredient, Recipes, Tag
from api.mixins import AddDelViewMixin
from api.paginators import PageLimitPagination
from api.permissions import (
    AdminOrReadOnly,
    AuthorStaffOrReadOnly,
    DjangoModelPermissions,
    IsAuthenticated,
)
from api.serializers import (
    IngredientSerializer,
    RecipesSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserSubscribeSerializer,
)
from core.enums import Tuples, UrlQueries
from core.services import create_shoping_list




class BaseAPIRootView(APIRootView):
    """Базовые пути API приложения."""


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """
    Работает с пользователями.

    ViewSet для работы с пользователми - вывод таковых,
    регистрация.
    Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """

    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """
        Создаёт/удалет связь между пользователями.
        """

    @subscribe.mapping.post
    def create_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._delete_relation(Q(author__id=id))

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: WSGIRequest) -> Response:
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

    def get_queryset(self) -> list[Ingredient]:
        """
        Получение queryset в соответствии с параметрами запроса.
        """
        name: str = self.request.query_params.get(UrlQueries.SEARCH_ING_NAME)
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

    queryset = Recipes.objects.select_related('author')
    serializer_class = RecipesSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    pagination_class = PageLimitPagination
    add_serializer = ShortRecipeSerializer

    def get_queryset(self) -> QuerySet[Recipes]:
        """
        Получение queryset в соответствии с параметрами запроса.
        """
        queryset = self.queryset

        tags: list = self.request.query_params.getlist(UrlQueries.TAGS.value)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author: str = self.request.query_params.get(UrlQueries.AUTHOR.value)
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return queryset

        is_in_cart: str = self.request.query_params.get(UrlQueries.SHOP_CART)
        if is_in_cart in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_carts__user=self.request.user)
        elif is_in_cart in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        is_favorite: str = self.request.query_params.get(UrlQueries.FAVORITE)
        if is_favorite in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorite in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request: WSGIRequest, pk: int | str) -> Response:
        """
        Добавляем/удалем рецепт в `избранное`.
        """

    @favorite.mapping.post
    def recipe_to_favorites(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Favorites
        return self._create_relation(pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Favorites
        return self._delete_relation(Q(recipe__id=pk))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        """
        Добавляем/удалем рецепт в `список покупок`.
        """

    @shopping_cart.mapping.post
    def recipe_to_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        self.link_model = Carts
        return self._create_relation(pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Carts
        return self._delete_relation(Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
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





################
#def send_confirmation_code(user):
#    confirmation_code = default_token_generator.make_token(user)
#    send_mail(
#        subject='YaMDb registration',
#        message=f'Your confirmation code: {confirmation_code}',
#        from_email=FROM_EMAIL,
#        recipient_list=[user.email],
#    )


#@api_view(['POST'])
#@permission_classes([permissions.AllowAny])
#def registration(request):
#    """Регистрация нового пользователя."""
#    username_check = request.data.get('username')
#    email_check = request.data.get('email')
#    if User.objects.filter(username=username_check,
#                           email=email_check).exists():
#        user_exists = get_object_or_404(
#            User, username=username_check, email=email_check
#        )
#        serializer = RegistrationDataSerializer(user_exists)
#        send_confirmation_code(user_exists)
#        return Response(serializer.data, status=status.HTTP_200_OK)

#    serializer = RegistrationDataSerializer(data=request.data)
#    serializer.is_valid(raise_exception=True)
#    serializer.save()
#    user, created = User.objects.get_or_create(
#        username=serializer.validated_data['username']
#    )
#    send_confirmation_code(user)
#    return Response(serializer.data, status=status.HTTP_200_OK)


#@api_view(['POST'])
#@permission_classes([permissions.AllowAny])
#def get_jwt_token(request):
#    """Выдача токена пользователю."""
#    serializer = TokenSerializer(data=request.data)
#    serializer.is_valid(raise_exception=True)
#    user = get_object_or_404(
#        User,
#        username=serializer.validated_data['username']
#    )
#    if default_token_generator.check_token(
#        user, serializer.validated_data['confirmation_code']
#    ):
#        token = AccessToken.for_user(user)
#        return Response({'token': str(token)}, status=status.HTTP_200_OK)

 #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#class UserViewSet(viewsets.ModelViewSet):
#    """Вьюсет для обьектов модели User."""
#    filter_backends = (filters.SearchFilter,)
#    search_fields = ('username',)
#    lookup_field = 'username'
#    queryset = User.objects.all()
#    serializer_class = UserSerializer
#    permission_classes = (IsAdmin,)
#    http_method_names = ['get', 'post', 'patch', 'delete']

#    @action(
#        methods=['get', 'patch'],
#        detail=False,
#        permission_classes=[permissions.IsAuthenticated],
#        serializer_class=UserEditSerializer,
#    )
#    def me(self, request):
#        user = request.user
#        if request.method == 'GET':
#            serializer = self.get_serializer(user)
#            return Response(serializer.data, status=status.HTTP_200_OK)
#        serializer = self.get_serializer(
#            user,
#            data=request.data,
#            partial=True
#        )
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_200_OK)

