from PIL import Image
from django.db import models
# from django.contrib.auth import get_user_model
from users.models import User
####
from core.enums import Tuples
# from django.db.models.functions import Length
# CharField.register_lookup(Length)


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
        max_length=50,
        unique=True,
        db_index=False,
    )
    color = models.CharField(
        verbose_name='Цвет',
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
        max_length=20
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
#        constraints = (
#            models.UniqueConstraint(
#                fields=('name', 'measurement_unit',),
#                name='unique_for_ingredient',
#            ),
#        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipes(models.Model):
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
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта',
        null=True,
    )

    tag = models.ManyToManyField(
        Tag,
        # blank=True, null=True,
        verbose_name='Тэг',
        related_name='recipes',
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        blank=True,
        # null=True,
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipesIngredient',
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        # validators= ?
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

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.thumbnail(Tuples.RECIPE_IMAGE_SIZE)
        image.save(self.image.path)


class RecipesIngredient(models.Model):
    """
    Количество ингридиентов в блюде.
    Модель связывает Recipe и Ingredient с указанием количества ингридиента.
    """
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Необходимые ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0
        # validators= min-max ?
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipes',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipes', 'ingredients'),
                name='Ingredient alredy added',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class FavoriteRecipes(models.Model):
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
        Recipes,
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
        return f'{self.user} -> {self.recipe}'


class Carts(models.Model):
    """
    Модель рецептов в корзине покупок.
    """

    recipes = models.ForeignKey(
        Recipes,
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
