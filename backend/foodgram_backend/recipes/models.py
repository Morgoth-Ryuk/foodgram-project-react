from django.db import models
from django.contrib.auth import get_user_model
from users.models import User


class Tag(models.Model):
    """
    Модель Tag.
    """
    title = models.CharField(
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
        ordering = ('title',)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    """
    name = models.CharField(
        'Название ингредиента',
        max_length=50
    )
    measurement_unit =  models.CharField(
        'Единицы измерения',
        max_length=20
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


#class Recipes(models.Model):
#    """
#    Модель рецептов.
#    """
#    name = models.CharField('Название блюда',
#                             max_length=200)
#    text = models.TextField(
#       verbose_name='Текст рецепта',
#       help_text='Введите описание рецепта'
#    )
#    pub_date = models.DateTimeField(
#        verbose_name='Дата публикации',
#        auto_now_add=True,
#        editable=False,)
    #quantity = DecimalField(decimal_places=10, max_digits=5)
#    author = models.ForeignKey(
#        to=User,
#        on_delete=models.SET_NULL,
#        related_name='recipes',
#        verbose_name='Автор рецепта',
#        help_text='Укажите автора рецепта'
#    )

#    tag = models.ManyToManyField(
#        Tag,
#        #blank=True, null=True,
#        on_delete=models.SET_NULL,
#        verbose_name='Тэг',
#        related_name='recipes',
#    )

#    image = models.ImageField(
#        'Картинка',
#        upload_to='recipes/images/',
#        blank=True,
#        #null=True,
#    )

#    ingredients = models.ManyToManyField(
#        Ingredient, through='RecipesIngredient',
#        verbose_name="Ингредиенты блюда",
#        related_name="recipes",
#    )

#    cooking_time = PositiveSmallIntegerField(
#        verbose_name="Время приготовления",
#        default=0,
#        validators=(
#            MinValueValidator(
#                Limits.MIN_COOKING_TIME.value,
#                "Ваше блюдо уже готово!",
#            ),
#            MaxValueValidator(
#                Limits.MAX_COOKING_TIME.value,
#                "Очень долго ждать...",
#            ),
#        ),
#    )
#
#    class Meta:
#        ordering = ('-pub_date',)
#        verbose_name = 'Рецепт'
#        verbose_name_plural = 'Рецепты'

#    def __str__(self):
#        return '{title}, {text}, {date:%Y-%m-%d}, {author}, {tag}'.format(
#            text=self.text[:15],
#            date=self.pub_date,
#            author=self.author.username,
#            tag=self.tag,
 #           title=self.title
  #      )


#class RecipesIngredient(models.Model):
 #   recipes = models.ForeignKey(Pizza)
  #  ingredient = models.ForeignKey(Ingredient)
   # quantity = models.DecimalField(max_digits=10, decimal_places=5)
    #unit = models.CharField(max_length=30)  # Единица измерения (граммы, ложки). Надо выделить в отдельную таблицу?

    #class Meta:
     #   unique_together = (('pizza', 'ingredient'),)


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