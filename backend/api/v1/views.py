from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from djoser.views import UserViewSet

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404

from recipes.models import Recipe, Tag, Ingredient, ShoppingList, FavoriteRecipe
from .serializers import (RecipeSerializer, TagSerializer,
                          IngredientSerializer,
                          CustomUserSerializer, FollowSerializer, ShortRecipeSerializer)
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientSearchFilter
from .shopping_list import get_ingredients
from users.models import User, Follow


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        instance = FavoriteRecipe.objects.filter(user=request.user, recipe__id=pk)
        if request.method == 'POST' and not instance.exists():
            recipe = get_object_or_404(Recipe, id=pk)
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Рецепт не найден'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        instance = ShoppingList.objects.filter(
            user=request.user.id,
            recipe__id=pk
        )
        if request.method == 'POST' and not instance.exists():
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingList.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = get_ingredients(request.user)
        html_template = render_to_string('shopping_cart.html',
                                         {'ingredients': ingredients})
        html = HTML(string=html_template)
        result = html.write_pdf()
        response = HttpResponse(result, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        return response


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'list' or 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        return super(CustomUserViewSet, self).me(request, *args, **kwargs)


class FollowView(APIView):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return Response(
                {'error': 'Нельзя подписаться на себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на пользователя!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
