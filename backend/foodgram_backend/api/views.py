from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny

from datetime import date

from django.db.models import Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404

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
#from api.mixins import AddDelViewMixin
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
    SubscriptionCreateSerializer,
    SubscriptionsSerializer,
    CartSerializer,
    RecipeInCartSerializer,
    FavoriteRecipeSerializer
)


class UserViewSet(DjoserUserViewSet):
    # , AddDelViewMixin):
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
                serializer.save()
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
        return Response(
            {'errors': 'Подписка удалена'},
            status=status.HTTP_404_NOT_FOUND
        )

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


class RecipeViewSet(ModelViewSet):
    # , AddDelViewMixin):
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

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated,]
    )
    def add_in_favorite(self, request, pk):
        """Добавление рецептов в избранное."""

        recipes = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(
                data={'user': request.user.id, 'recipes': recipes.id}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_serializer = FavoriteRecipeSerializer(recipes)
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        favorite_recipe = get_object_or_404(
            FavoriteRecipe, user=request.user, recipes=recipes
        )
        favorite_recipe.delete()
        return Response({'errors': 'Рецепт успешно удалён из избранного.'},
                        status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart',
            url_name='shopping_cart',
            permission_classes=[IsAuthenticated])
    def add_in_cart(self, request, pk):
        """
        Добавить/Удалить  рецепт из списка покупок.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user

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
                response_create = RecipeInCartSerializer(recipe)
                return Response(response_create.data,
                                status=status.HTTP_201_CREATED)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if not Carts.objects.filter(
            user=user,
            recipes=recipe
        ).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        Carts.objects.get(recipes=recipe).delete()
        return Response({'errors': 'Рецепт успешно удалён из списка покупок.'},
                        status=status.HTTP_200_OK)

    @action(
        methods=['get',],
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


class CartViewSet(ModelViewSet):
    """
    Работает с корзиной.
    """
    queryset = Carts.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AuthorStaffOrReadOnly]
    pagination_class = PageLimitPagination
