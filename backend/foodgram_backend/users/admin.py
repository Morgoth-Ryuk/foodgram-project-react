from django.contrib import admin
from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Регистрация и настройка отображения модели User в админке.
    """
    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'bio',
    )
    list_editable = ('username','email','bio',)
    search_fields = ('username','email')
    list_filter = ('username','email','role',)
    empty_value_display = '-пусто-'