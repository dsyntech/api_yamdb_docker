from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb import settings
from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    TitleReadSerializer, TitleWriteSerializer, TokenAuthSerializer,
    UserSerializer,
)


class NameSlugCreateListDestroyViewSet(mixins.CreateModelMixin,
                                       mixins.ListModelMixin,
                                       mixins.DestroyModelMixin,
                                       GenericViewSet):
    """
    View Set with only Create, List and Destroy functionality.
    It is expected that serializer provides 'slug', 'name' fields.
    """
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('slug', 'name')
    lookup_field = 'slug'


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_email(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get('email')
    username = email.replace('@', '-').replace('.', '-')
    user = serializer.save(username=username, is_active=False)
    token = default_token_generator.make_token(user=user)
    send_mail(
        subject='Подтверждение регистрации',
        message=f'Код для подтверждения: {token}',
        from_email=settings.EMAIL_NAME,
        recipient_list=(email,)
    )
    return Response({'message': f'Код отправлен на {email}'},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_token(request):
    serializer = TokenAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=request.data.get('email'))
    token = request.data.get('confirmation_code')
    if default_token_generator.check_token(user, token):
        refresh = RefreshToken.for_user(user)
        user.is_active = True
        user.save()
        return Response({'token': str(refresh.access_token)})
    return Response({'message': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = self.serializer_class(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.serializer_class(user, data=request.data,
                                               partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
            return Response(serializer.data)


class CategoryViewSet(NameSlugCreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(NameSlugCreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(ModelViewSet):
    permission_classes = (IsAuthorOrModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly,)
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrReadOnly,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)
