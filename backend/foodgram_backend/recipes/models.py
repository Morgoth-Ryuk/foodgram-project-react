from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    """
    Модель Tag.
    """
    name = models.CharField(
        verbose_name='Название тэга',
        max_length=20,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Короткая ссылка',
        max_length=20,
        unique=True,
        db_index=False,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    """
    name = models.CharField(
        'Название ингредиента',
        max_length=100
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}'


class Recipe(models.Model):
    """
    Модель рецептов.
    """
    name = models.CharField(
        'Название блюда',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Введите описание рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        blank=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author',),
                name='unique_for_author',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()


class IngredientInRecipe(models.Model):
    """
    Количество ингридиентов в блюде.
    Модель связывает Recipe и Ingredient с указанием количества ингридиента.
    """
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredients_used',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Необходимые ингредиенты',
        related_name='recipes_used',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=[MinValueValidator(0), ]
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='Ingredient alredy added',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredient}'


class FavoriteRecipe(models.Model):
    """
    Модель избранных рецептов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
        help_text='Кто хочет подписаться',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Понравившиеся рецепты',
        help_text='Рецепт, который хотите добавить в избранное',
    )

    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipes', 'user'),
                name='Recipe is favorite alredy',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipes}'


class Carts(models.Model):
    """
    Модель рецептов в корзине покупок.
    """

    recipes = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        related_name='in_carts',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Владелец списка покупок',
        related_name='carts',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('recipes', 'user'),
                name='Recipe is cart alredy',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipes}'
