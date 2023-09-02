from pathlib import Path

from django.db.models.signals import post_delete
from django.dispatch import receiver
from recipes.models import Recipes


@receiver(post_delete, sender=Recipes)
def delete_image(sender: Recipes, instance: Recipes, *a, **kw) -> None:
    """
    Удаляет картинку при удаление рецепта. 
    """
    image = Path(instance.image.path)
    if image.exists():
        image.unlink()
