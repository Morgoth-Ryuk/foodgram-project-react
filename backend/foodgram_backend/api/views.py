from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import filters
#from django_filters.rest_framework import DjangoFilterBackend
from foodgram_backend.settings import FROM_EMAIL
from users.models import User
from api.permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAdminModeratorOwnerOrReadOnly
)
from api.serializers import (
    RegistrationDataSerializer, TokenSerializer,
    UserEditSerializer, UserSerializer
)



def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='YaMDb registration',
        message=f'Your confirmation code: {confirmation_code}',
        from_email=FROM_EMAIL,
        recipient_list=[user.email],
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registration(request):
    """Регистрация нового пользователя."""
    username_check = request.data.get('username')
    email_check = request.data.get('email')
    if User.objects.filter(username=username_check,
                           email=email_check).exists():
        user_exists = get_object_or_404(
            User, username=username_check, email=email_check
        )
        serializer = RegistrationDataSerializer(user_exists)
        send_confirmation_code(user_exists)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = RegistrationDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user, created = User.objects.get_or_create(
        username=serializer.validated_data['username']
    )
    send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """Выдача токена пользователю."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    if default_token_generator.check_token(
        user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели User."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

