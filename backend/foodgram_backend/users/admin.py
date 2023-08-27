from django.contrib import admin
from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Регистрация и настройка отображения модели User в админке.
    """
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    #list_editable = ('username','email')
    search_fields = ('username','email')
    list_filter = ('username','email')
    empty_value_display = '-пусто-'