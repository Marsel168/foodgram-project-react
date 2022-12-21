from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .v1.views import (RecipeViewSet, IngredientViewSet,
                       TagViewSet, CustomUserViewSet,
                       FollowView, FollowListView)
from djoser.views import TokenCreateView, TokenDestroyView

router_v1 = DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('users/subscriptions/', FollowListView.as_view(), name='subscription'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('users/<int:user_id>/subscribe/', FollowView.as_view(), name='subscribe'),
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view()),
]
