
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from core.services import recipe_ingredients_set
from recipes.models import Ingredient, Recipe, Tag, IngredientInRecipe

from djoser.serializers import UserSerializer, UserCreateSerializer


class ShortRecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели Recipes с укороченным набором полей.
    """

    class Meta:
        model = Recipe
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


class UserSubscribeSerializer(CustomUserSerializer):
    """
    Вывод авторов на которых подписан текущий пользователь.
    """

    recipe = ShortRecipeSerializer(many=True, read_only=True)
    # recipes_count = SerializerMethodField()

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
            # 'recipes_count',
        )
        read_only_fields = ('__all__',)

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


class IngredientM2MSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    # amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = IngredientInRecipe
        read_only_fields = ('id',)


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при GET запросах."""
    
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    IngredientM2MSerializer(many=True, source='ingredients_used')
    #is_favorited = serializers.SerializerMethodField(read_only=True)
    #is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipesCreateSerializer(ModelSerializer):
    """
    Сериализатор для рецептов.
    Update/Create
    """

    tags = TagSerializer(many=True, read_only=True)
    #tags = serializers.PrimaryKeyRelatedField(
    #    queryset=Tag.objects.all(), many=True
    #)
    author = UserSerializer(read_only=True)
    ingredients = IngredientM2MSerializer(many=True, source='ingredients_used') 
    #is_favorited = SerializerMethodField()
    #is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

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
            #'is_favorited',
            #'is_in_shopping_cart',
        )
        #read_only_fields = (
        #    'is_favorite',
        #    'is_shopping_cart',
        #)

    def create(self, validated_data):
        """
        Создаёт рецепт.
        """
        ingredients = validated_data.pop('ingredients_used')
        # tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        #recipe.tags.set(tags)

        for ingredient in ingredients:
            current_ingredient = ingredient.get('ingredient')
            amount = ingredient.get('amount')
            recipe.ingredients.add(
                current_ingredient,
                through_defaults={
                    'amount': amount,
                }
            )
        return recipe

    def get_ingredients(self, recipe):
        """
        Получает список ингридиентов для рецепта.
        """
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients
    
    def to_representation(self, recipe):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipeGETSerializer(recipe)
        return serializer.data

    #def get_is_favorited(self, recipe: Recipes) -> bool:
    #    """
    #    Проверка - находится ли рецепт в избранном.
    #    """
    #    user = self.context.get('view').request.user

    #    if user.is_anonymous:
    #        return False
    #    return user.favorites.filter(recipe=recipe).exists()

    #def get_is_in_shopping_cart(self, recipe: Recipes) -> bool:
    #    """
    #    Проверка - находится ли рецепт в списке  покупок.
    #    """
    #    user = self.context.get('view').request.user

    #    if user.is_anonymous:
    #        return False

    #    return user.carts.filter(recipe=recipe).exists()


    def update(self, recipe: Recipe, validated_data: dict):
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
