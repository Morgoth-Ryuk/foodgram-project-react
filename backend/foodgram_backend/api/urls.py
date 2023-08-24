from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (UserViewSet, get_jwt_token, registration)


router = DefaultRouter()
router.register(r'users', UserViewSet)
#router.register(r'recipes', RecipesViewSet)
#router.register(r'achievements', AchievementViewSet)

auth_urls = [
    path('signup/', registration, name='registration'),
    path('token/', get_jwt_token, name='token'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urls)),
]

#if settings.DEBUG:
    #urlpatterns += static(settings.MEDIA_URL,
                          #document_root=settings.MEDIA_ROOT)

