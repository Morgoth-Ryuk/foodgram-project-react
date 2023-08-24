from django.db import models
from django.contrib.auth import get_user_model
#from users.models import User

#class Unit(models.Model):
    #"""
    #Модель единиц измерения.
    #"""
    #pass


#class Tag(models.Model):
 #   """
  #  Модель Tag.
   # """
    #title = models.CharField('Название тэга',
    #                         max_length=20)
    #slug = models.SlugField('Короткая ссылка',
    #                        max_length=50, unique=True)
    #color = models.CharField(max_length=16)

    #class Meta:
    #    verbose_name = 'Тэг'
    #    verbose_name_plural = 'Тэги'

    #def __str__(self):
    #    return self.title


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    """
    name = models.CharField('Название ингредиента',
                             max_length=50)
    measurement_unit =  models.CharField('Единицы измерения', max_length=20)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


#class Recipes(models.Model):
#    """
#    Модель рецептов.
#    """
#    title = models.CharField('Название рецепта',
#                             max_length=200)
#    text = models.TextField('Текст рецепта',
#                            help_text='Введите описание рецепта')
#    pub_date = models.DateTimeField(
#        'Дата публикации',
#        auto_now_add=True)
    #quantity = DecimalField(decimal_places=10, max_digits=5)
#    author = models.ForeignKey(
#        User,
#        on_delete=models.CASCADE,
#        related_name='recipes',
#        verbose_name='Автор',
#        help_text='Укажите автора рецепта'
#    )

#    tag = models.ManyToManyField(
#        Tag,
#        blank=True, null=True,
#        on_delete=models.SET_NULL,
#    )

#    image = models.ImageField(
#        'Картинка',
#        upload_to='recipes/images/',
#        blank=True,
#        #null=True,
#    )

#    ingredients = models.ManyToManyField(Ingredient, through='RecipesIngredient')
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