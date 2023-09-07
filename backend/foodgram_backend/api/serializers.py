
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from core.services import recipe_ingredients_set
from recipes.models import Ingredient, Recipes, Tag

from djoser.serializers import UserSerializer, UserCreateSerializer


class ShortRecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели Recipes с укороченным набором полей.
    """

    class Meta:
        model = Recipes
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ('__all__',)


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для модели User профилей.
    """

    is_subscribed = SerializerMethodField(read_only=True)

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
        extra_kwargs = {"password": {"write_only": True}}

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Проверка подписки пользователей.
        """
        user = self.context.get('request').user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data: dict) -> User:
        """
        Создаёт нового пользователя с запрошенными полями.
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Регистрация пользователя foodgram.
    Переопределение дефолтного UserCreateSerializer в djoser.
    Эндпоинты:
        * POST api/users/
    """
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password')
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с указанным username'
            )
        return value


class UserSubscribeSerializer(CustomUserSerializer):
    """
    Вывод авторов на которых подписан текущий пользователь.
    """

    recipe = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

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

    # def get_is_subscribed(*args) -> bool:
        # """
        # Проверка подписки пользователей.
        # """
        # return True

    def get_recipes_count(self, obj: User) -> int:
        """
        Подсчет общего количества рецептов у каждого автора.
        """
        return obj.recipes.count()


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipesSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, recipe: Recipes) -> QuerySet[dict]:
        """
        Получает список ингридиентов для рецепта.
        """
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipes) -> bool:
        """
        Проверка - находится ли рецепт в избранном.
        """
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipes) -> bool:
        """
        Проверка - находится ли рецепт в списке  покупок.
        """
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False

        return user.carts.filter(recipe=recipe).exists()

    @atomic
    def create(self, validated_data: dict) -> Recipes:
        """
        Создаёт рецепт.
        """
        tags: list[int] = validated_data.pop('tags')
        ingredients: dict[int, tuple] = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe

    @atomic
    def update(self, recipe: Recipes, validated_data: dict):
        """
        Обновляет рецепт.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe


# class RegistrationDataSerializer(UserSerializer):
    # """Права на доступ администратору и модератору либо только на чтение."""

    # class Meta:
    #     fields = ('username', 'email')
    #     model = User


# class TokenSerializer(serializers.Serializer):
    # username = serializers.CharField()
    # confirmation_code = serializers.CharField()
