from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny

from django.db.models import Q, QuerySet
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404

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
    CustomUserSerializer,
    UserSubscribeSerializer,
    RecipeReadSerializer,
    SubscriptionCreateSerializer,
    SubscriptionsSerializer,
)
from api.services import create_shoping_list


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """
    Работа с пользователями.
    """
    serializer_class = UserSubscribeSerializer
    http_method_names = ('get', 'post', 'delete')
    queryset = User.objects.all()

    pagination_class = PageLimitPagination
    permission_classes = (AllowAny,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,))

    def subscribe(self, request, id):
        """
        Создаёт/удалет подписку.
        """
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': request.user.id, 'author': author.id})

            if serializer.is_valid(raise_exception=True):
                serializer.save()   #(author=author, user=request.user)
                response_create = SubscriptionsSerializer(
                    author, context={'request': request}
                )
                return Response(
                    response_create.data,
                    status=status.HTTP_201_CREATED)
                
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        subscription = get_object_or_404(
            Subscription, user=request.user, author=author
        )
        subscription.delete()
        return Response({'errors': 'Подписка удалена'}, status=status.HTTP_404_NOT_FOUND)


    @action(
        detail=False,
        methods=['get',],
        permission_classes=(IsAuthenticated,)
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
        Получение queryset.
        """
        name = self.request.query_params.get('name')
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
    

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def add_in_cart(self, request):
        """
        Получить / Добавить / Удалить  рецепт
        из списка покупок у текущего пользоватля.
        """
        recipe = get_object_or_404(Recipe, id=self.request.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            if Carts.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = CartSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if not Carts.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
                            
        Carts.objects.get(recipe=recipe).delete()
        return Response('Рецепт успешно удалён из списка покупок.',
                        status=status.HTTP_204_NO_CONTENT)


    @action(
        methods=['get',],
        detail=False,
        permission_classes=[IsAuthenticated])
    def download_cart(self, request):
        """
        Формирует файл *.txt со списком покупок.
        """
        recipe = get_object_or_404(Recipe, id=self.request.get('pk'))
        user = self.request.user

        if not user.carts.exists():
            return Response(
                'Список покупок пуст.',
                status=status.HTTP_404_NOT_FOUND)

        #filename = f'{user.username}_shopping_list.txt'
        shopping_list = create_shoping_list(user)
        return shopping_list
