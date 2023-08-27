from django.db import models
from django.contrib.auth import get_user_model
from users.models import User


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
        max_length=50
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=20
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_for_ingredient',
            ),
        )
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
   #quantity = DecimalField(decimal_places=10, max_digits=5)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта'
    )

    tag = models.ManyToManyField(
        Tag,
        #blank=True, null=True,
        verbose_name='Тэг',
        related_name='recipes',
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        blank=True,
        #null=True,
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipesIngredient',
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
    )

    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        #validators= ?
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            UniqueConstraint(
                fields=['name', 'author'],
                name='unique_for_author',
            )
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'



class RecipesIngredient(models.Model):
    """Количество ингридиентов в блюде.
    Модель связывает Recipe и Ingredient с указанием количества ингридиента.
    """
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Необходимые ингредиенты',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0
        #validators= min-max ?
    )
   
    class Meta:
       unique_together = (('pizza', 'ingredient'),)
       class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipes',)
        constraints = (
            UniqueConstraint(
                fields=['recipes','ingredients'],
                name='Ingredient alredy added',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


#class FavoriteRecipes(models.Model):
 #   """
  #  Модель избранных рецептов.
   # """
    #user = models.ForeignKey(
     #   User,
      #  on_delete=models.CASCADE,
       # related_name='follower',
        #verbose_name='Подписчик',
        #help_text='Кто хочет подписаться',
    #)
    #recipes = models.ForeignKey(
    #    User,
    #    on_delete=models.CASCADE,
    #    related_name='favorite',
    #    verbose_name='Рецепт',
    #    help_text='Рецепт, который хотите добавить в избранное',
    #)

    #class Meta:
    #    verbose_name = 'Избранное'
    #    verbose_name_plural = 'Избранные'
    #    constraints = [
    #        models.UniqueConstraint(
     #           fields=['user', 'recipes'], name='unique_follow'
      #      )
       # ]

    #def __str__(self):
    #    return '{user}, {recipes}'.format(
    #        recipes=self.recipes.title,
    #        user=self.user.username
    #    )

#class Follow(models.Model):
 #   """
  #  Модель подписки.
   # """
    #user = models.ForeignKey(
     #   User,
      #  on_delete=models.CASCADE,
       # related_name='follower',
        #verbose_name='Подписчик',
        #help_text='Кто хочет подписаться',
    #)
    #author = models.ForeignKey(
     #   User,
      #  on_delete=models.CASCADE,
       # related_name='following',
        #verbose_name='Автор',
        #help_text='Автор, на которого хотите подписаться',
    #)

    #class Meta:
     #   verbose_name = 'Подписка'
      #  verbose_name_plural = 'Подписки'
       # constraints = [
        #    models.UniqueConstraint(
         #       fields=['user', 'author'], name='unique_follow'
          #  )
        #]

    #def __str__(self):
     #   return '{user}, {author}'.format(
      #      author=self.author.username,
       #     user=self.user.username
        #)