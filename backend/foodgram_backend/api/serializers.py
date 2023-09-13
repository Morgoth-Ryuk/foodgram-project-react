
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from users.models import User, Subscription
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    IngredientInRecipe,
    Carts,
    FavoriteRecipe
)

from djoser.serializers import UserSerializer, UserCreateSerializer


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для модели User профилей.
    """

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj: User):
        """
        Проверка подписки пользователей.
        """
        user = self.context.get('request').user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Регистрация пользователя foodgram.
    Переопределение дефолтного UserCreateSerializer в djoser.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с указанным username'
            )
        return value


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class FavoriteRecipeSerializer(ModelSerializer):
    """Сериализатор для записи рецепта в Избранное.
    Работа с моделью FavoriteRecipe."""

    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

    def get_is_favorited(self, recipe: Recipe):
        """
        Отметка рецепт в избранном.
        """
        return True


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для показа рецептов из избранного."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('__all__',)


class RecipesIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    def get_amount(self, obj):
        return obj.amount


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при GET запросах."""

    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = RecipesIngredientsReadSerializer(
        many=True,
        read_only=True,
        source='ingredients_used'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, recipe: Recipe):
        """
        Проверка - находится ли рецепт в избранном.
        """
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipes=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe):
        """
        Проверка - находится ли рецепт в списке  покупок.
        """
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False
        return Carts.objects.filter(user=request.user, recipes=recipe).exists()


class IngredientM2MSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        fields = ('id', 'amount')
        model = IngredientInRecipe
        read_only_fields = ('id',)


class RecipesCreateSerializer(ModelSerializer):
    """
    Сериализатор для рецептов.
    Update/Create
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientM2MSerializer(many=True, source='ingredients_used')
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        """
        Создаёт рецепт.
        """
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            recipe.ingredients.add(
                ingredient.get('id'),
                through_defaults={
                    'amount': ingredient.get('amount'),
                }
            )
        return recipe

    def to_representation(self, recipe):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipeReadSerializer(recipe)
        return serializer.data

    def update(self, recipe, validated_data):
        """
        Обновляет рецепт.
        """
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients_used', None)

        if tags is not None:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients is not None:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient.get('amount')
                ingredient_instance = ingredient.get('id').id
                ingredient = get_object_or_404(
                    Ingredient,
                    pk=ingredient_instance
                )

                IngredientInRecipe.objects.update_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
        return super().update(recipe, validated_data)

    def get_is_favorited(self, recipe: Recipe):
        """
        Проверка - находится ли рецепт в избранном.
        """
        return False

    def get_is_in_shopping_cart(self, recipe: Recipe):
        """
        Проверка - находится ли рецепт в списке  покупок.
        """
        return False


class UserSubscribeSerializer(CustomUserSerializer):
    """
    Вывод авторов на которых подписан текущий пользователь.
    """

    recipe = RecipeReadSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipe',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_recipes_count(self, obj: User):
        """
        Подсчет общего количества рецептов у каждого автора.
        """
        return obj.recipes.count()

    def get_is_subscribed(self, obj: User):
        """
        Проверка подписки пользователей.
        """
        return True


class SubscriptionCreateSerializer(ModelSerializer):
    """
    Создание подписки.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('__all__',)

    def get_is_subscribed(self, obj: User):
        return True


class SubscriptionsSerializer(ModelSerializer):
    """
    Вывод ответа о совершении подписки.
    """

    # recipes = serializers.SerializerMethodField()
    recipes = ShortRecipeSerializer()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')

    def get_is_subscribed(self, obj):
        """
        Проставление отметки о подписке
        """
        return True

    def get_recipes(self, obj):
        author_recipes = obj.recipes.all()[:5]
        return ShortRecipeSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, obj):
        """
        Подсчет общего количества рецептов у каждого автора.
        """
        return obj.recipes.count()


class CartSerializer(ModelSerializer):
    """
    Работа с корзиной покупок.
    """
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )

    class Meta:
        model = Carts
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
