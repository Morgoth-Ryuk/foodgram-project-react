from datetime import date

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.db.models import Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from foodgram_backend.settings import DATE_TIME_FORMAT
from users.models import User, Subscription
from recipes.models import (
    Carts,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    Tag,
    IngredientInRecipe
)
from api.paginators import LimitPagination
from api.filters import RecipeFilter
from api.permissions import (
    AdminOrReadOnly,
    AuthorStaffOrReadOnly,
)
from api.serializers import (
    IngredientSerializer,
    RecipesCreateUpdateSerializer,
    TagSerializer,
    CustomUserSerializer,
    RecipeReadSerializer,
    SubscriptionCreateSerializer,
    SubscriptionsSerializer,
    CartSerializer,
    FavoriteRecipeSerializer,
    ShortRecipeSerializer
)


class UserViewSet(DjoserUserViewSet):
    """
    Работа с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ('get', 'post', 'delete')

    pagination_class = LimitPagination
    permission_classes = (AllowAny,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, id):
        """
        Создаёт/удалет подписку.
        """

        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':

            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    data={'detail': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = SubscriptionCreateSerializer(
                data={'user': request.user.id, 'author': author.id}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, author=author)
                response_create = SubscriptionsSerializer(
                    author, context={'request': request}
                )
                return Response(
                    response_create.data,
                    status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Subscription, user=request.user, author=author
        )
        subscription.delete()
        return Response(
            {'errors': 'Подписка удалена'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        """
        Список подписок пользоваетеля.
        """

        queryset = User.objects.filter(subscribers__user=request.user)
        pag_queryset = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pag_queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=[IsAuthenticated, ]
    )
    def get_me(self, request):
        """Позволяет получить информацию о себе."""

        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ReadOnlyModelViewSet):
    """
    Работает с тэгами.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Работет с игридиентами.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None

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


class RecipeViewSet(ModelViewSet):
    """
    Работает с рецептами.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipesCreateUpdateSerializer
    permission_classes = [AuthorStaffOrReadOnly]
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipesCreateUpdateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def add_in_favorite(self, request, pk):
        """Добавление рецептов в избранное."""

        recipes = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                user=request.user,
                recipes=recipes
            ).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = FavoriteRecipeSerializer(
                data={
                    'user': request.user.id,
                    'recipes': recipes.id
                }
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipes=recipes)
                response_serializer = ShortRecipeSerializer(
                    recipes
                )
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )

        if not FavoriteRecipe.objects.filter(
            user=request.user,
            recipes=recipes
        ).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        FavoriteRecipe.objects.get(
            user=request.user,
            recipes=recipes
        ).delete()
        return Response({'errors': 'Рецепт успешно удалён из избранного.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart',
            url_name='shopping_cart',
            permission_classes=[IsAuthenticated, AuthorStaffOrReadOnly])
    def add_in_cart(self, request, pk):
        """
        Добавить/Удалить  рецепт из списка покупок.
        """

        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if Carts.objects.filter(
                user=user,
                recipes=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = CartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipes=recipe)
                response_create = ShortRecipeSerializer(recipe)
                return Response(response_create.data,
                                status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        if not Carts.objects.filter(
            user=user,
            recipes=recipe
        ).exists():
            return Response(
                {'detail': 'Рецепта еще нет в списке покупок!'},
                status=status.HTTP_404_NOT_FOUND
            )

        Carts.objects.get(
            user=user,
            recipes=recipe
        ).delete()
        return Response({'errors': 'Рецепт успешно удалён из списка покупок.'},
                        status=status.HTTP_200_OK)

    @action(
        methods=['get', ],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=[IsAuthenticated])
    def download_cart(self, request):
        """
        Cформировать и скачать список покупок.
        """

        user = User.objects.get(id=self.request.user.pk)

        today = date.today().strftime(DATE_TIME_FORMAT)
        shopping_list = [
            f'Список покупок {request.user.first_name}\n'
            f'{today}\n'
        ]

        ingredients_in_cart = (
            IngredientInRecipe.objects.filter(
                recipe__in_carts__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).annotate(amount=Sum(
                'amount', distinct=True
            )).order_by('ingredient__name')
        )
        for ingredient in ingredients_in_cart:
            shopping_list += (
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )

        filename = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
